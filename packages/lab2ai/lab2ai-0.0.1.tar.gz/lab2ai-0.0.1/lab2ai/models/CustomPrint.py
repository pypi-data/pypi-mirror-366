from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED, MINIMAL
from rich.style import Style

class CustomPrint:
    def __init__(self):
        self.console = Console()
    
    def create_panel(self, content, title=None, border_style="white", box=ROUNDED, padding=(1, 1), title_align="left", expand=False):
        return Panel(
            content,
            title=title,
            box=box,
            padding=padding,
            border_style=border_style,
            title_align=title_align,
            expand=expand
        )

    def create_table(self, header_style=Style(color="#FFFFFF", bold=True)):
        table = Table(
            show_header=True,
            header_style=header_style,
            box=MINIMAL,
            show_lines=True,
            expand=False,
            border_style="white",
            padding=(0, 0)
        )
        table.add_column("Options", style=Style(color="#7B7B7B"), no_wrap=True)
        table.add_column("Description", style=Style(color="#FFFFFF"))
        return table

    def add_parser_actions_to_table(self, table, parser):
        for action in parser._actions:
            if action.option_strings:
                options = ", ".join(action.option_strings)
                table.add_row(options, action.help or "")

    def custom_help(self, parser):
        header_panel = self.create_panel(
            Text('Auxiliary tools for Rankadmet', style="white"),
            title="lab2ai v0.0.1",
        )

        main_table = self.create_table()
        self.add_parser_actions_to_table(main_table, parser)
        main_panel = self.create_panel(main_table, title="Main Commands", padding=(0, 0))

        footer_panel = self.create_panel(
            Text("""
LAMBDA - Laboratório Multiusuário de Bioinformática e Análise de Dados
Júlio César Albuquerque Xavier
Edson Luiz Folador
""", justify="center"),
            box=MINIMAL,
            expand=True,
            padding=(0, 0)
        )

        panels = ["\n", header_panel, main_panel, footer_panel, "\n"]
        for panel in panels:
            self.console.print(panel)

    def custom_print(self, text, title):
        panel = self.create_panel(
            Text(text, justify="left"),
            title=title,
            padding=(1, 2, 0, 2)
        )
        self.console.print(panel)