from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from typing import List, Tuple

def print_unmerged_blocks(unmerged_blocks: List[Tuple]):
    console = Console()
    console.print("\n[bold red]Unmerged Blocks:[/bold red]")
    for file_path, head, update, similarity in unmerged_blocks:
        console.print(f"\n[bold blue]File:[/bold blue] {file_path}")
        console.print(f"\n[bold green]Search Block({similarity}):[/bold green]")
        syntax = Syntax(head, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, expand=False))
        console.print("\n[bold yellow]Replace Block:[/bold yellow]")
        syntax = Syntax(update, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, expand=False))
    console.print(
        f"\n[bold red]Total unmerged blocks: {len(unmerged_blocks)}[/bold red]"
    )