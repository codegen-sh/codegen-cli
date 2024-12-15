from pathlib import Path
import click
from rich import box
from rich.console import Console
from rich.panel import Panel

from codegen.analytics.decorators import track_command
from codegen.auth.decorator import requires_auth, requires_init
from codegen.auth.session import CodegenSession


@click.command(name="profile")
@track_command()
@requires_auth
@requires_init
def profile_command(session: CodegenSession):
    """Display information about the currently authenticated user."""
    console = Console()

    console.print(
        Panel(
            f"[cyan]Name:[/cyan]  {session.profile.name}\n" f"[cyan]Email:[/cyan] {session.profile.email}\n" f"[cyan]Repo:[/cyan]  {session.repo_name}",
            title="🔑 [bold]Current Profile[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    # Show active codemod if one exists
    active_codemod = session.active_codemod
    if active_codemod:
        content = []
        content.append("📝 [bold]Active Codemod[/bold]\n")
        content.append(f"[cyan]Name:[/cyan] {active_codemod.name}")
        content.append(f"[cyan]Path:[/cyan] {active_codemod.relative_path()}")
        content.append(f"[cyan]URL:[/cyan] {active_codemod.get_url()}")

        if active_codemod.config:
            content.append(f"[cyan]ID:[/cyan]   {active_codemod.config.codemod_id}")
            if active_codemod.config.description:
                content.append(f"[cyan]Desc:[/cyan] {active_codemod.config.description}")

        # Show the source code
        source = active_codemod.path.read_text()
        content.append("\n[bold]Source Code:[/bold]")

        # Create source code panel
        source_panel = Panel(
            source,
            title="[bold blue]run.py",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        content.append(source_panel.renderable)

        console.print(
            Panel(
                "\n".join(str(line) for line in content),
                title="[bold]Active Codemod Details[/bold]",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
