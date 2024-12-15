import click
from rich.console import Console
from rich.panel import Panel
from rich import box

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

    console.print("\n🔑 [bold]Current Profile:[/bold]")
    console.print("─" * 40)
    console.print(f"[cyan]Name:[/cyan]  {session.profile.name}")
    console.print(f"[cyan]Email:[/cyan] {session.profile.email}")
    console.print(f"[cyan]Repo:[/cyan]  {session.repo_name}")

    # Show active codemod if one exists
    active_codemod = session.active_codemod
    if active_codemod:
        console.print("\n📝 [bold]Active Codemod:[/bold]")
        console.print(f"[cyan]Name:[/cyan] {active_codemod.name}")
        console.print(f"[cyan]URL:[/cyan] {active_codemod.get_url()}")
        console.print(f"[cyan]Path:[/cyan] {active_codemod.path}")

        if active_codemod.config:
            console.print(f"[cyan]ID:[/cyan]   {active_codemod.config.codemod_id}")
            if active_codemod.config.description:
                console.print(f"[cyan]Desc:[/cyan] {active_codemod.config.description}")

        # Show the source code
        source = active_codemod.path.read_text()
        console.print("\n[bold]Source Code:[/bold]")
        console.print(
            Panel(
                source,
                title="[bold blue]run.py",
                border_style="blue",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

    console.print("─" * 40 + "\n")
