import webbrowser
from pathlib import Path

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
from codegen.rich.pretty_print import pretty_print_output
from codegen.utils.git.patch import apply_patch


@click.command(name="run")
@track_command()
@requires_auth
@requires_init
@click.option("--web", is_flag=True, help="Automatically open the diff in the web app")
@click.option("--apply-local", is_flag=True, help="Applies the generated diff to the repository")
def run_command(session: CodegenSession, codemod_path: Path | None = None, repo_path: Path | None = None, web: bool = False, apply_local: bool = False):
    """Run code transformation on the provided Python code."""
    if not session.active_codemod:
        raise click.ClickException("No codemod path provided and no active codemod found.\n" "Either provide a codemod path or create one with: codegen create <name>")

    console = Console()
    status = Status("Running codemod...", spinner="dots", spinner_style="purple")
    status.start()

    # Print details below the spinner
    console.print(
        Panel(
            f"[cyan]Repo:[/cyan]    {session.repo_name}\n" f"[cyan]Codemod:[/cyan] {session.active_codemod.name}",
            title="🔧 [bold]Running Codemod[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    try:
        run_output = API.run(
            codemod=session.active_codemod,
            repo_full_name=session.repo_name,
        )

        status.stop()
        console.print("✓ Codemod run complete", style="green")

        pretty_print_output(run_output)

        if web and run_output.web_link:
            webbrowser.open_new(run_output.web_link)

        if apply_local and run_output.observation:
            apply_patch(session.git_repo, f"\n{run_output.observation}\n")
            click.echo(f"Diff applied to {session.git_repo.path}")

    except ServerError as e:
        status.stop()
        raise click.ClickException(str(e))
    finally:
        status.stop()
