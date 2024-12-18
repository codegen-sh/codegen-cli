import rich_click as click
from rich import box
from rich.console import Console
from rich.panel import Panel

from codegen.analytics.decorators import track_command
from codegen.auth.decorators import requires_auth
from codegen.auth.session import CodegenSession
from codegen.commands.set_active.render import display_codemods_table
from codegen.utils.codemod_manager import CodemodManager
from codegen.workspace.decorators import requires_init


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
        display_codemods_table(console, codemods, session, current_page, per_page)

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
