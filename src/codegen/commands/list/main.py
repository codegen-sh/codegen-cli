import rich
import rich_click as click
from rich.table import Table

from codegen.analytics.decorators import track_command
from codegen.auth.decorators import requires_auth
from codegen.auth.session import CodegenSession
from codegen.utils.codemod_manager import CodemodManager
from codegen.workspace.decorators import requires_init


@click.command(name="list")
@track_command()
@requires_auth
@requires_init
def list_command(session: CodegenSession):
    """List all available codemods."""
    codemods = CodemodManager.list()

    if not codemods:
        rich.print("[yellow]No codemods found.[/yellow]")
        rich.print("\nCreate one with:")
        rich.print("  [blue]codegen create <name>[/blue]")
        return

    table = Table(title="Available Codemods", border_style="blue")
    table.add_column("Name", style="cyan")
    table.add_column("Active", style="yellow")

    for codemod in codemods:
        name = codemod.name
        is_active = "✓" if session.active_codemod and session.active_codemod.name == name else ""
        table.add_row(name, is_active)

    rich.print(table)
    rich.print("\nRun a codemod with:")
    rich.print("  [blue]codegen run <name>[/blue]")
