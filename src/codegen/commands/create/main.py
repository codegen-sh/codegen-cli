from pathlib import Path

import rich
import rich_click as click
from rich import box
from rich.panel import Panel
from rich.status import Status

from codegen.analytics.decorators import track_command
from codegen.api.client import RestAPI
from codegen.auth.decorators import requires_auth
from codegen.auth.session import CodegenSession
from codegen.codemod.convert import convert_to_cli
from codegen.errors import ServerError
from codegen.utils.codemod_manager import CodemodManager
from codegen.utils.constants import ProgrammingLanguage
from codegen.utils.schema import CODEMOD_CONFIG_PATH
from codegen.workspace.decorators import requires_init


@click.command(name="create")
@track_command()
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
            codemod_name = CodemodManager.get_valid_name(name)
            text = f"""[bold red]🔴 Failed to generate codemod[/bold red]: Codemod `{codemod_name}` already exists at {CodemodManager.CODEMODS_DIR / codemod_name}
[bold yellow]🧠 Hint[/bold yellow]: Overwrite codemod with `--overwrite` or choose a different name."""
            rich.print(
                Panel(
                    text,
                    title="Error Generating Codemod",
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )
            rich.print()
            return

    if description:
        status_message = "[bold]Generating codemod (using LLM, this will take ~30s)..."
    else:
        status_message = "[bold]Setting up codemod..."

    with Status(status_message, spinner="dots", spinner_style="purple") as status:
        try:
            # Get code from API
            response = RestAPI(session.token).create(description if description else None)
            # Show the AI's explanation
            rich.print("\n[bold]🤖 AI Assistant:[/bold]")
            rich.print(
                Panel(
                    response.response,
                    title="[bold blue]Generated Codemod Explanation",
                    border_style="blue",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )

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
    if overwrote_codemod:
        rich.print(f"\n[bold green]✨ Overwrote codemod {codemod.name} successfully:[/bold green]")
    else:
        rich.print(f"\n[bold green]✨ Created codemod {codemod.name} successfully:[/bold green]")
    rich.print("─" * 40)
    rich.print(f"[cyan]Location:[/cyan] {make_relative(codemod.path.parent)}")
    rich.print(f"[cyan]Main file:[/cyan] {make_relative(codemod.path)}")
    rich.print(f"[cyan]Name:[/cyan] {codemod.name}")
    rich.print(f"[cyan]Helpful hints:[/cyan] {make_relative(codemod.get_system_prompt_path())}")
    if codemod.config:
        rich.print(f"[cyan]Config:[/cyan] {make_relative(codemod.path.parent / CODEMOD_CONFIG_PATH)}")
    rich.print("\n[bold yellow]💡 Next steps:[/bold yellow]")
    rich.print("1. Review and edit [cyan]run.py[/cyan] to customize the codemod")
    rich.print(f"2. Run it with: [green]codegen run {name}[/green]")
    rich.print("─" * 40 + "\n")
