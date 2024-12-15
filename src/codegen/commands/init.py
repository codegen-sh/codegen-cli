from pathlib import Path

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


def get_success_message(codegen_folder, codemods_folder, docs_folder, examples_folder, sample_codemod_path) -> Text:
    """Create a rich-formatted success message."""
    message = Text()

    # Folders section
    message.append("\n📁 ", style="bold yellow")
    message.append("Folders Created:", style="bold blue")
    message.append(f"\n   • Codegen:  ", style="dim")
    message.append(str(codegen_folder), style="cyan")
    message.append(f"\n   • Codemods: ", style="dim")
    message.append(str(codemods_folder), style="cyan")
    message.append(f"\n   • Docs:     ", style="dim")
    message.append(str(docs_folder), style="cyan")
    message.append(f"\n   • Examples: ", style="dim")
    message.append(str(examples_folder), style="cyan")

    # Sample codemod section
    message.append("\n\n📝 ", style="bold yellow")
    message.append("Sample Codemod:", style="bold blue")
    message.append("\n   ", style="dim")
    message.append(str(sample_codemod_path), style="cyan")

    # Getting started section
    message.append("\n\n🔨 ", style="bold yellow")
    message.append("Getting Started:", style="bold blue")
    message.append("\n   1. Add your codemods to the codemods folder")
    message.append("\n   2. Run them with: ", style="dim")
    message.append("codegen run --codemod <path>", style="green")
    message.append("\n   3. Try the sample: ", style="dim")
    message.append(f"codegen run --codemod {sample_codemod_path}", style="green")

    # Tips section
    message.append("\n\n💡 ", style="bold yellow")
    message.append("Tips:", style="bold blue")
    message.append("\n   • Use absolute paths for all arguments")
    message.append("\n   • Codemods use the graph_sitter library")
    message.append("\n   • Run ", style="dim")
    message.append("codegen docs_search", style="green")
    message.append(" for examples and documentation", style="dim")

    return message


@click.command(name="init")
@track_command()
@requires_auth
def init_command(session: CodegenSession):
    """Initialize or update the Codegen folder."""
    codegen_dir = Path.cwd() / ".codegen"
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
    console.print("\n")
