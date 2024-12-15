import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.status import Status

from codegen.analytics.decorators import track_command
from codegen.api.client import API
from codegen.auth.decorator import requires_auth, requires_init
from codegen.auth.session import CodegenSession
from codegen.errors import ServerError
from codegen.utils.codemods import CodemodManager


@click.command(name="create")
@track_command()
@requires_auth
@requires_init
@click.argument("name", type=str)
@click.option("--description", "-d", default=None, help="Description of what this codemod does")
def create_command(session: CodegenSession, name: str, description: str | None):
    """Create a new codemod in the .codegen/codemods directory."""
    console = Console()

    with Status("[bold]Generating codemod...", spinner="dots", spinner_style="purple") as status:
        try:
            # Get code from API
            response = API.create(description if description else None)

            # Show the AI's explanation
            console.print("\n[bold]🤖 AI Assistant:[/bold]")
            console.print(
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
                name=name,
                code=response.code,
                codemod_id=response.codemod_id,
                description=description or f"AI-generated codemod for: {name}",
                author=session.profile.name,
            )

        except ServerError as e:
            status.stop()
            raise click.ClickException(str(e))
        except ValueError as e:
            status.stop()
            raise click.ClickException(str(e))

    # Success message
    console.print("\n[bold green]✨ Created new codemod:[/bold green]")
    console.print("─" * 40)
    console.print(f"[cyan]Location:[/cyan] {codemod.path.parent}")
    console.print(f"[cyan]Main file:[/cyan] {codemod.path}")
    if codemod.config:
        console.print(f"[cyan]Config:[/cyan] {codemod.path.parent / 'config.json'}")
    console.print("\n[bold yellow]💡 Next steps:[/bold yellow]")
    console.print("1. Review and edit [cyan]run.py[/cyan] to customize the codemod")
    console.print("2. Run it with: [green]codegen run[/green]")
    console.print("─" * 40 + "\n")
