import rich_click as click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from codegen.analytics.decorators import track_command
from codegen.auth.decorator import requires_auth, requires_init
from codegen.auth.session import CodegenSession
from codegen.utils.codemod_manager import CodemodManager
from codegen.utils.codemods import Codemod


def display_codemods_table(console: Console, codemods: list[Codemod], page: int, per_page: int = 10) -> None:
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
            "✓" if codemod.is_active else "",
        )

    console.print(table)

    # Print navigation help
    if total_pages > 1:
        console.print("\n[dim]Use arrow keys to navigate pages, Enter to select, or type number to jump to codemod[/dim]")


@click.command(name="set-active")
@track_command()
@requires_auth
@requires_init
def set_active_command(session: CodegenSession):
    """Interactively select the active codemod."""
    console = Console()
    codemods = CodemodManager.list()

    if not codemods:
        raise click.ClickException("No codemods found. Create one first with: codegen create <name>")

    # Initialize pagination
    current_page = 0
    per_page = 10
    total_pages = (len(codemods) + per_page - 1) // per_page
    while True:
        console.clear()
        console.print("\n[bold]Select Active Codemod[/bold]\n")
        display_codemods_table(console, codemods, current_page, per_page)

        # Get user input
        choice = click.prompt(
            "\nEnter codemod number, [n]ext, [p]rev, or [q]uit",
            type=str,
            default="",
        ).lower()

        if choice == "q":
            return

        elif choice == "n":
            if current_page < total_pages - 1:
                current_page += 1

        elif choice == "p":
            if current_page > 0:
                current_page -= 1

        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(codemods):
                selected_codemod = codemods[idx]

                # Set as active
                session.state.active_codemod = selected_codemod.name
                session.write_state()
                console.print(
                    Panel(
                        f"[green]✓ Set active codemod to:[/green] {selected_codemod.name}\n" f"[dim]You can now use 'codegen run' to run this codemod[/dim]",
                        title="[bold green]Success!",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(1, 2),
                    )
                )
                return
            else:
                console.print("[red]Invalid codemod number[/red]")
                click.pause()

        else:
            console.print("[red]Invalid input[/red]")
            click.pause()
