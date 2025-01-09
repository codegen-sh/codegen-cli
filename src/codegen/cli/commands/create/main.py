from pathlib import Path

import rich
import rich_click as click

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.codemod.convert import convert_to_cli
from codegen.cli.errors import ServerError
from codegen.cli.rich.codeblocks import format_command, format_path
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.codemod_manager import CodemodManager
from codegen.cli.utils.constants import ProgrammingLanguage
from codegen.cli.utils.schema import CODEMOD_CONFIG_PATH
from codegen.cli.workspace.decorators import requires_init


@click.command(name="create")
@requires_auth
@requires_init
@click.argument("name", type=str, required=False)
@click.option("--description", "-d", default=None, help="Description of what this codemod does.")
@click.option("--overwrite", is_flag=True, help="Overwrites codemod if it already exists.")
def create_command(session: CodegenSession, name: str, description: str | None = None, overwrite: bool = False):
    """Create a new codemod in the codegen-sh/codemods directory."""
    overwrote_codemod = False
    if CodemodManager.exists(name=name):
        if overwrite:
            overwrote_codemod = True
        else:
            rich.print("\n[bold red]Error:[/bold red] Codemod already exists")
            rich.print(f"[white]Codemod `{name}` already exists at {format_path(str(CodemodManager.CODEMODS_DIR / name))}[/white]")
            rich.print("[dim]To overwrite the codemod:[/dim]")
            rich.print(f"{format_command(f'codegen create {name} --overwrite')}")
            return

    if description:
        status_message = "Generating codemod (using LLM, this will take ~30s)"
    else:
        status_message = "Setting up codemod"

    rich.print("")  # Add a newline before the spinner
    with create_spinner(status_message) as status:
        try:
            # Get code from API
            response = RestAPI(session.token).create(description if description else None)

            # Create the codemod
            codemod = CodemodManager.create(
                session=session,
                name=name,
                # TODO - this is wrong, need to fetch this language or set it properly
                code=convert_to_cli(response.code, session.config.programming_language or ProgrammingLanguage.PYTHON),
                codemod_id=response.codemod_id,
                description=description or f"AI-generated codemod for: {name}",
                author=session.profile.name,
                system_prompt=response.context,
            )

        except ServerError as e:
            status.stop()
            raise click.ClickException(str(e))
        except ValueError as e:
            status.stop()
            raise click.ClickException(str(e))

    def make_relative(path: Path) -> str:
        return f"./{path.relative_to(Path.cwd())}"

    # Success message
    rich.print(f"\n✅ {'Overwrote' if overwrote_codemod else 'Created'} codemod {codemod.name}")
    rich.print("")
    rich.print("📁 Files Created:")
    rich.print(f"   📦 Location:  {make_relative(codemod.path.parent)}")
    rich.print(f"   🔧 Main file: {make_relative(codemod.path)}")
    rich.print(f"   📚 Hints:     {make_relative(codemod.get_system_prompt_path())}")
    if codemod.config:
        rich.print(f"   ⚙️  Config:    {make_relative(codemod.path.parent / CODEMOD_CONFIG_PATH)}")

    # Next steps
    rich.print("\n[bold]What's next?[/bold]")
    rich.print("1. Review and edit run.py to customize the codemod")
    rich.print(f"2. Run it with: \n{format_command(f'codegen run {name}')}")
