import os
import subprocess
import difflib
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from typing import List, Tuple
from rich.live import Live
from rich.text import Text

def print_unmerged_blocks(unmerged_blocks: List[Tuple], language: str = "python"):
    """
    Prints the unmerged blocks of code with syntax highlighting.

    :param unmerged_blocks: A list of tuples containing file path, search block, replace block, and similarity score.
    :param language: The programming language of the code blocks, default is "python".
    """
    console = Console()
    console.print("\n[bold red]Unmerged Blocks:[/bold red]")
    for file_path, head, update, similarity in unmerged_blocks:
        console.print(f"\n[bold blue]File:[/bold blue] {file_path}")
        console.print(f"\n[bold green]Search Block({similarity}):[/bold green]")
        syntax = Syntax(head, language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, expand=False))
        console.print("\n[bold yellow]Replace Block:[/bold yellow]")
        syntax = Syntax(update, language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, expand=False))
    console.print(
        f"\n[bold red]Total unmerged blocks: {len(unmerged_blocks)}[/bold red]"
    )

def print_diff_blocks(unmerged_blocks: List[Tuple], language: str = "python"):
    console = Console()
    console.print("\n[bold red]Unmerged Blocks as Diff:[/bold red]")
    for file_path, head, update, similarity in unmerged_blocks:
        console.print(f"\n[bold blue]File:[/bold blue] {file_path}")
        console.print(f"[bold blue]Similarity:[/bold blue] {similarity}")
        diff = difflib.unified_diff(
            head.splitlines(),
            update.splitlines(),
            fromfile='a/' + os.path.relpath(file_path, start=os.getcwd()),
            tofile='b/' + os.path.relpath(file_path, start=os.getcwd()),
            lineterm='',
        )
        diff_text = "\n".join(diff)
        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, expand=False))
    console.print(
        f"\n[bold red]Total unmerged blocks: {len(unmerged_blocks)}[/bold red]"
    )

def execute_shell_command(command: str):
    console = Console()
    try:
        # Use shell=True to support shell mode
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=True,
        )

        output = []
        with Live(console=console, refresh_per_second=4) as live:
            while True:
                output_line = process.stdout.readline()
                error_line = process.stderr.readline()

                if output_line:
                    output.append(output_line.strip())
                    live.update(
                        Panel(
                            Text("\n".join(output[-20:])),
                            title="Shell Output",
                            border_style="green",
                        )
                    )
                if error_line:
                    output.append(f"ERROR: {error_line.strip()}")
                    live.update(
                        Panel(
                            Text("\n".join(output[-20:])),
                            title="Shell Output",
                            border_style="red",
                        )
                    )

                if (
                    output_line == ""
                    and error_line == ""
                    and process.poll() is not None
                ):
                    break

        if process.returncode != 0:
            console.print(
                f"[bold red]Command failed with return code {process.returncode}[/bold red]"
            )
        else:
            console.print("[bold green]Command completed successfully[/bold green]")

    except FileNotFoundError:
        console.print(
            f"[bold red]Command not found:[/bold red] [yellow]{command}[/yellow]"
        )
    except subprocess.SubprocessError as e:
        console.print(
            f"[bold red]Error executing command:[/bold red] [yellow]{str(e)}[/yellow]"
        )
