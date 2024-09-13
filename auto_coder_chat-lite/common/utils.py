def print_diff_blocks(unmerged_blocks: List[Tuple], language: str = "python"):
    console = Console()
    console.print("\n[bold red]Unmerged Blocks as Diff:[/bold red]")
    for file_path, head, update, similarity in unmerged_blocks:
        console.print(f"\n[bold blue]File:[/bold blue] {file_path} [bold green]Similarity: {similarity}[/bold green]")  # 将 File 和 Similarity 放在同一行
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