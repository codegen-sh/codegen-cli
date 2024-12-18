import rich
import rich_click as click
from rich import box
from rich.panel import Panel

from codegen.analytics.decorators import track_command
from codegen.auth.decorators import requires_auth
from codegen.auth.session import CodegenSession
from codegen.workspace.decorators import requires_init


@click.command(name="profile")
@track_command()
@requires_auth
@requires_init
def profile_command(session: CodegenSession):
    """Display information about the currently authenticated user."""
    rich.print(
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
        content.append(f"[cyan]Name:[/cyan] {active_codemod.name}")
        content.append(f"[cyan]Path:[/cyan] {active_codemod.relative_path()}")

        if active_codemod.config:
            if active_codemod.config.codemod_id:
                content.append(f"[cyan]ID:[/cyan]   {active_codemod.config.codemod_id}")
            if active_codemod.config.description:
                content.append(f"[cyan]Desc:[/cyan] {active_codemod.config.description}")

        rich.print(
            Panel(
                "\n".join(str(line) for line in content),
                title="[bold]Active Codemod[/bold]",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
