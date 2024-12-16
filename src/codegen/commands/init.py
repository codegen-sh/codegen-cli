import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.text import Text

from codegen.analytics.decorators import track_command
from codegen.auth.decorator import requires_auth
from codegen.auth.session import CodegenSession
from codegen.utils.init import initialize_codegen


def get_success_message(codegen_folder, codemods_folder, docs_folder, examples_folder) -> Text:
    """Create a rich-formatted success message."""
    message = Text()

    # Folders section
    message.append("\n📁 ", style="bold yellow")
    message.append("Folders Created:", style="bold blue")
    message.append("\n   • Codegen:  ", style="dim")
    message.append(str(codegen_folder), style="cyan")
    message.append("\n   • Codemods: ", style="dim")
    message.append(str(codemods_folder), style="cyan")
    message.append("\n   • Docs:     ", style="dim")
    message.append(str(docs_folder), style="cyan")
    message.append("\n   • Examples: ", style="dim")
    message.append(str(examples_folder), style="cyan")

    return message


@click.command(name="init")
@track_command()
@requires_auth
def init_command(session: CodegenSession):
    """Initialize or update the Codegen folder."""
    codegen_dir = session.codegen_dir

    is_update = codegen_dir.exists()

    console = Console()
    action = "Updating" if is_update else "Initializing"
    with Status(f"[bold]{action} Codegen...", spinner="dots", spinner_style="purple") as status:
        folders = initialize_codegen(status, is_update=is_update)

    # Print success message
    console.print("\n")
    console.print(
        Panel(
            get_success_message(*folders),
            title=f"[bold green]🚀 Codegen CLI {action} Successfully!",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    # Print next steps panel
    console.print("\n")
    console.print(
        Panel(
            "[bold white]Create a codemod with:[/bold white]\n\n"
            '[cyan]\tcodegen create my-codemod-name --description "describe what you want to do"[/cyan]\n\n'
            "[dim]This will create a new codemod in the codegen-sh/codemods folder.[/dim]\n\n"
            "[bold white]Then run it with:[/bold white]\n\n"
            "[cyan]\tcodegen run --apply-local[/cyan]\n\n"
            "[dim]This will apply your codemod and show you the results.[/dim]",
            title="[bold white ]✨ What's Next?[/bold white]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print("\n")
