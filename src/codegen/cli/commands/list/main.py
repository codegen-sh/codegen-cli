from pathlib import Path

import rich
import rich_click as click
from rich.table import Table

from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.rich.codeblocks import format_code, format_command
from codegen.cli.utils.codemod_manager import CodemodManager
from codegen.cli.workspace.decorators import requires_init


@click.command(name="list")
@requires_auth
@requires_init
@click.option("--decorated", is_flag=True, help="Only show decorated functions found in the current directory")
@click.option("--stored", is_flag=True, help="Only show stored codemods")
def list_command(session: CodegenSession, decorated: bool = False, stored: bool = False):
    """List available codemods and decorated functions."""
    # If neither flag is set, show both
    show_all = not decorated and not stored

    if show_all or stored:
        # Show stored codemods
        codemods = CodemodManager.list()
        if codemods:
            table = Table(title="Stored Codemods", border_style="blue")
            table.add_column("Name", style="cyan")
            table.add_column("Path", style="dim")

            for codemod in codemods:
                table.add_row(codemod.name, str(codemod.relative_path()))

            rich.print(table)
            rich.print("\nRun a stored codemod with:")
            rich.print(format_command("codegen run <name>"))
        elif show_all:
            rich.print("[yellow]No stored codemods found.[/yellow]")
            rich.print("\nCreate one with:")
            rich.print(format_command("codegen create <name>"))

    if show_all and codemods:
        rich.print()  # Add spacing between tables

    if show_all or decorated:
        # Show decorated functions
        functions = CodemodManager.get_decorated()
        if functions:
            table = Table(title="Decorated Functions", border_style="blue")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Path", style="dim")

            for func in functions:
                func_type = "Webhook" if func.lint_mode else "Function"
                table.add_row(func.name, func_type, str(func.filepath.relative_to(Path.cwd())) if func.filepath else "<unknown>")

            rich.print(table)
            rich.print("\nRun a decorated function with:")
            rich.print(format_command("codegen run {function-label}"))
        elif show_all:
            rich.print("[yellow]No decorated functions found in current directory.[/yellow]")
            rich.print("\nAdd a function with @codegen.function decorator:")
            rich.print(format_code("@codegen.function('label')"))
