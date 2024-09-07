from typing import List
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import git

class GitDiffExtractor:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)

    def extract_git_diff(self, ai_response: str) -> List[str]:
        """
        Extract git diff blocks from the AI response.
        """
        diff_blocks = []
        lines = ai_response.splitlines()
        in_diff_block = False
        diff_block = []

        for line in lines:
            if line.startswith("```diff"):
                in_diff_block = True
                continue
            if line.startswith("```") and in_diff_block:
                in_diff_block = False
                diff_blocks.append("\n".join(diff_block))
                diff_block = []
                continue
            if in_diff_block:
                diff_block.append(line)

        return diff_blocks

    def apply_patch(self, diff_blocks: List[str]) -> bool:
        """
        Apply the extracted git diff blocks using GitPython.
        """
        try:
            for diff_block in diff_blocks:
                self.repo.git.apply(diff_block, check=True)
            return True
        except git.GitCommandError as e:
            logger.error(f"Failed to apply patch: {e}")
            return False

    def _print_unmerged_blocks(self, unmerged_blocks: List[tuple]):
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