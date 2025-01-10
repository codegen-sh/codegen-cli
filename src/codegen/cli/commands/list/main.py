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
def list_command(session: CodegenSession):
    """List available codegen functions."""
    functions = CodemodManager.get_decorated()
    if functions:
        table = Table(title="Codegen Functions", border_style="blue")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Path", style="dim")

        for func in functions:
            func_type = "Webhook" if func.lint_mode else "Function"
            table.add_row(func.name, func_type, str(func.filepath.relative_to(Path.cwd())) if func.filepath else "<unknown>")

        rich.print(table)
        rich.print("\nRun a function with:")
        rich.print(format_command("codegen run <label>"))
    else:
        rich.print("[yellow]No codegen functions found in current directory.[/yellow]")
        rich.print("\nAdd a function with @codegen.function decorator:")
        rich.print(format_code("@codegen.function('label')"))
