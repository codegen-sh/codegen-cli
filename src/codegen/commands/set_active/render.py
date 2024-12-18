from rich import box
from rich.console import Console
from rich.table import Table

from codegen.auth.session import CodegenSession
from codegen.utils.codemods import Codemod


def display_codemods_table(console: Console, codemods: list[Codemod], session: CodegenSession, page: int, per_page: int = 10) -> None:
    """Display a table of codemods with pagination."""
    # Calculate pagination
    start_idx = page * per_page
    end_idx = start_idx + per_page
    total_pages = (len(codemods) + per_page - 1) // per_page

    # Create table
    table = Table(
        show_header=True,
        header_style="bold blue",
        box=box.ROUNDED,
        title=f"Page {page + 1} of {total_pages}",
    )

    # Add columns
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Author", style="yellow")
    table.add_column("Active", justify="center", width=8)

    # Add rows for current page
    page_codemods = codemods[start_idx:end_idx]
    for idx, codemod in enumerate(page_codemods, start=start_idx + 1):
        table.add_row(
            str(idx),
            codemod.name,
            codemod.config.description if codemod.config else "No description",
            codemod.config.created_by if codemod.config else "Unknown",
            "✓" if codemod.name == session.state.active_codemod else "",
        )

    console.print(table)

    # Print navigation help
    if total_pages > 1:
        console.print("\n[dim]Use arrow keys to navigate pages, Enter to select, or type number to jump to codemod[/dim]")
