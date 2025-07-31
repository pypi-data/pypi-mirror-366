import sys
import pandas as pd
from openbabel import pybel
from rich.console import Console
from rich.progress import *
import argparse
import os
import datetime
from typing import List
from contextlib import contextmanager
from .models.CustomPrint import CustomPrint
import glob
from rankadmet import RankAdmet, Output

console = Console()

@contextmanager
def suppress_stderr():
    stderr_fd = sys.stderr.fileno()
    saved_stderr_fd = os.dup(stderr_fd)
    try:
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, stderr_fd)
        os.close(devnull_fd)
        yield
    finally:
        os.dup2(saved_stderr_fd, stderr_fd)
        os.close(saved_stderr_fd)

def create_parsers() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Auxiliary tools for Rankadmet', add_help=False)
    
    parser.add_argument('-i', '--input', type=str, nargs='+', help='Input file(s) or folder(s). Default mode accepts Excel files to convert AdmetLab spreadsheets into an AdmetAI spreadsheet. Use flags for SDF mode.')
    parser.add_argument('-p', '--property', type=str, default='minimizedAffinity', help='[SDF Mode] Property to sort by (default: minimizedAffinity).')
    parser.add_argument('-bs', '--batchsize', type=int, default=299, help='[SDF Mode] Batch size for splitting SDF files (default: 299).')
    parser.add_argument('--smiles', action='store_true', help='[SDF Mode] Creates a CSV file with SMILES strings from input SDF file(s).')
    parser.add_argument('--split', action='store_true', help='[SDF Mode] Splits input SDF file(s) into smaller chunks, and creates a CSV with the SMILES of all molecules in the SDF.')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit.')
    parser.add_argument('-v', '--version', action='version', version='lab2ai v0.0.1', help='Show the program version.')
    
    return parser

def find_sdf_files(input_paths: list) -> list:
    sdf_files = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True, console=console) as progress:
        task = progress.add_task("Searching for SDF files...", total=len(input_paths))
        for path in input_paths:
            if os.path.isdir(path):
                sdf_files.extend([os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.sdf')])
            elif os.path.isfile(path) and path.lower().endswith('.sdf'):
                sdf_files.append(path)
            progress.update(task, advance=1)
    return sdf_files

def count_molecules(sdf_files: list) -> int:
    total_molecules = 0
    with Progress(TextColumn("{task.description}"), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console=console) as progress:
        for sdf_file in sdf_files:
            try:
                with open(sdf_file, 'r', errors='ignore') as f:
                    total_molecules += f.read().count('$$$$')
            except IOError:
                console.print(f"[yellow]Warning:[/yellow] Could not read file '{sdf_file}' for counting.")
    return total_molecules

def sdf_to_dataframe(input_sdfs: list, property_key: str, output_dir: str, total_molecules: int) -> pd.DataFrame:
    data_rows = []
    property_found_in_any_mol = False

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Processing molecules for CSV...", total=total_molecules)

        for sdf_file in input_sdfs:
            try:
                with suppress_stderr():
                    for mol in pybel.readfile("sdf", sdf_file):
                        smiles = mol.write("smi").split('\t')[0]
                        full_title_string = mol.title
                        first_id = full_title_string.split()[0] if full_title_string else "NO_ID_FOUND"
                        
                        prop_value = None
                        if property_key in mol.data:
                            prop_value = mol.data[property_key]
                            property_found_in_any_mol = True
                        
                        data_rows.append([first_id, prop_value, smiles])
                        progress.update(task, advance=1)
            except Exception as e:
                console.print(f"[red]Error:[/red] Failed to process file '{sdf_file}': {e}", file=sys.stderr)
    
    if not data_rows:
        console.print(f"[red]Error:[/red] No molecules could be processed.")
        return pd.DataFrame()

    if property_found_in_any_mol:
        df = pd.DataFrame(data_rows, columns=["Id_Molecule", property_key, "smiles"])
        original_property_series = df[property_key].copy()
        df[property_key] = pd.to_numeric(df[property_key], errors='coerce')
        if df[property_key].isnull().all():
            console.print(f"[yellow]Warning:[/yellow] The property '{property_key}' could not be converted to a numeric type.")
            df[property_key] = original_property_series
        else:
            df.dropna(subset=[property_key], inplace=True)
            df.sort_values(by=property_key, ascending=True, inplace=True)
    else:
        df = pd.DataFrame([[row[0], row[2]] for row in data_rows], columns=["Id_Molecule", "smiles"])
        console.print(f"[yellow]Warning:[/yellow] The property '{property_key}' was not found in any molecule.")

    csv_filename = "combined_ranked_molecules.csv"
    full_output_path = os.path.join(output_dir, csv_filename)
    df.to_csv(full_output_path, index=False)
    
    return df

def batch_sdf_files(input_sdfs: list, batch_size: int, output_dir: str, total_molecules: int):
    if not total_molecules:
        console.print("[yellow]Warning:[/yellow] No molecules found to create batches.")
        return
    batch_files_created = 0
    molecule_count_in_batch = 0
    output_file = None
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Creating SDF batches...", total=total_molecules)   
        try:
            for sdf_file in input_sdfs:
                try:
                    with suppress_stderr():
                        for mol in pybel.readfile("sdf", sdf_file):
                            if molecule_count_in_batch == 0:
                                batch_files_created += 1
                                batch_filename = os.path.join(output_dir, f"batch_{batch_files_created}.sdf")
                                output_file = pybel.Outputfile("sdf", batch_filename, overwrite=True)
                            output_file.write(mol)
                            molecule_count_in_batch += 1
                            if molecule_count_in_batch >= batch_size:
                                output_file.close()
                                output_file = None
                                molecule_count_in_batch = 0
                            progress.update(task, advance=1)
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to process file '{sdf_file}' for batch creation: {e}", file=sys.stderr)
        finally:
            if output_file:
                with suppress_stderr():
                    output_file.close()
    console.print(f"Created {batch_files_created} batch file(s) in the '{output_dir}' directory.")

def conversion(excel_paths: List[str]) -> pd.DataFrame:
    all_dfs = []
    for path in excel_paths:
        if not os.path.exists(path):
            console.print(f"[bold red]Error:[/bold red] File '{path}' does not exist.")
            continue
        try:
            df = pd.read_excel(path)
            
            property_col_name = None
            if 'Property' in df.columns:
                property_col_name = 'Property'
            elif 'minimizedAffinity' in df.columns:
                property_col_name = 'minimizedAffinity'
            
            required_columns = ['ID_Molecula', 'smiles']
            if property_col_name:
                required_columns.insert(1, property_col_name)
            else:
                console.print(f"[bold yellow]Warning:[/bold yellow] File '{path}' is missing a property column ('Property' or 'minimizedAffinity').")
                continue

            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                console.print(f"[bold yellow]Warning:[/bold yellow] File '{path}' is missing columns: {missing_columns}")
                continue
            
            df = df[required_columns]
            df.columns = ['Id_Molecule', 'minimizedAffinity', 'smiles']
            all_dfs.append(df)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to process '{path}': {str(e)}")
            
    if not all_dfs:
        console.print("[bold red]Error:[/bold red] No valid data found in the provided Excel files.")
        return pd.DataFrame()
        
    final_df = pd.concat(all_dfs, ignore_index=True)
    return final_df


def mark_xlsx_as_processed(xlsx_path: str):
    """Renames a processed .xlsx file by appending '_done'."""
    if os.path.exists(xlsx_path):
        directory, original_filename = os.path.split(xlsx_path)
        base_name, extension = os.path.splitext(original_filename)
        new_filename = f"{base_name}_done{extension}"
        new_path = os.path.join(directory, new_filename)
        try:
            os.rename(xlsx_path, new_path)
        except OSError as e:
            console.print(f"  [red]Error:[/red] Failed to rename '{original_filename}': {e}", file=sys.stderr)
    else:
        console.print(f"  [yellow]Warning:[/yellow] File '{xlsx_path}' not found for renaming.")

def convert(input_paths: List[str]) -> None:
    top_hits = 50
    verbose = True

    all_potential_files = []
    for path in input_paths:
        if os.path.isdir(path):
            all_potential_files.extend(glob.glob(os.path.join(path, '*.xlsx')))
        elif os.path.isfile(path) and path.endswith('.xlsx'):
            all_potential_files.append(path)
        else:
            if verbose:
                console.print(f"[bold yellow]Warning:[/bold yellow] The input '{path}' is not a valid Excel file or directory. Skipping.")
            continue
            
    xlsx_files = []
    for f_path in all_potential_files:
        if '_done.xlsx' in os.path.basename(f_path).lower():
            if verbose:
                console.print(f"[yellow]Info:[/yellow] Skipping already processed file: '{os.path.basename(f_path)}'")
        else:
            xlsx_files.append(f_path)

    if not xlsx_files:
        if verbose:
            console.print(f"[bold red]Error:[/bold red] No valid Excel files found to process.")
        return
    
    rankadmet = RankAdmet(verbose=True)
    output = Output(output_dir=os.getcwd())

    total_files = len(xlsx_files)
    for i, input_xlsx in enumerate(xlsx_files, start=1):
        console.print(f"\n[bold blue]Processing file ({i}/{total_files}):[/] {os.path.basename(input_xlsx)}")
        df = conversion([input_xlsx])
        if df.empty:
            if verbose:
                console.print(f"[yellow]Warning:[/yellow] Skipped processing for '{os.path.basename(input_xlsx)}' as no valid molecules were read.")
            continue

        df = rankadmet.run(df)
        prop_col_name = df.columns[1]

        output.output_handled(df, top_hits, 'admetai', prop_col_name, verbose=True)
        
        mark_xlsx_as_processed(input_xlsx)


def mark_files_as_processed(sdf_files: list):
    for original_path in sdf_files:
        if os.path.exists(original_path):
            directory, original_filename = os.path.split(original_path)
            base_name, extension = os.path.splitext(original_filename)
            new_filename = f"{base_name}_ok{extension}"
            new_path = os.path.join(directory, new_filename)
            try:
                os.rename(original_path, new_path)
            except OSError as e:
                console.print(f"  [red]Error:[/red] Failed to rename '{original_filename}': {e}", file=sys.stderr)
        else:
            console.print(f"  [yellow]Warning:[/yellow] File '{original_path}' not found for renaming. It might have been moved or deleted.")

def main() -> None:
    parser = create_parsers()
    args = parser.parse_args()

    if args.input is None and not args.help:
        CustomPrint().custom_help(parser)
        return
    elif args.help:
        CustomPrint().custom_help(parser)
        return

    is_sdf_mode = args.smiles or args.split
    
    if is_sdf_mode:
        if args.smiles and args.split:
            console.print("[bold red]Error:[/bold red] The --smiles and --split parameters must be used exclusively.")
            return

        console.print("Running in SDF processing mode.")
        sdf_files = find_sdf_files(args.input)

        if not sdf_files:
            console.print(f"[bold red]Error:[/bold red] No SDF files found. This mode requires input files with the .sdf extension.")
            return
        
        console.print(f"Found {len(sdf_files)} SDF file(s) to process.")
        
        total_molecules = count_molecules(sdf_files)
        console.print(f"Found {total_molecules} molecules to process.")

        if total_molecules == 0:
            console.print("[yellow]Warning:[/yellow] No molecules found in the input SDF files. Exiting.")
            return

        timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        output_dir = f"rktool_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)

        if args.smiles:
            sdf_to_dataframe(sdf_files, args.property, output_dir, total_molecules)
        elif args.split:
            batch_sdf_files(sdf_files, args.batchsize, output_dir, total_molecules)
        
        mark_files_as_processed(sdf_files)

    else:
        convert(args.input)

if __name__ == '__main__':
    main()