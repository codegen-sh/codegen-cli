import rich
import rich_click as click
from rich import box
from rich.panel import Panel
from rich.status import Status

from codegen.analytics.decorators import track_command
from codegen.auth.decorators import requires_auth
from codegen.auth.session import CodegenSession
from codegen.commands.init.render import get_success_message
from codegen.git.url import get_git_organization_and_repo
from codegen.workspace.initialize_workspace import initialize_codegen


@click.command(name="init")
@track_command()
@click.option("--repo-name", type=str, help="The name of the repository")
@click.option("--organization-name", type=str, help="The name of the organization")
@requires_auth
def init_command(session: CodegenSession, repo_name: str | None = None, organization_name: str | None = None):
    """Initialize or update the Codegen folder."""
    codegen_dir = session.codegen_dir

    is_update = codegen_dir.exists()

    action = "Updating" if is_update else "Initializing"
    with Status(f"[bold]{action} Codegen...", spinner="dots", spinner_style="purple") as status:
        folders = initialize_codegen(status, is_update=is_update)
    if organization_name is not None:
        session.config.organization_name = organization_name
    if repo_name is not None:
        session.config.repo_name = repo_name
    if not session.config.organization_name or not session.config.repo_name:
        cwd_org, cwd_repo = get_git_organization_and_repo(session.git_repo)
        session.config.organization_name = session.config.organization_name or cwd_org
        session.config.repo_name = session.config.repo_name or cwd_repo
    session.write_config()
    rich.print(f"Organization name: {session.config.organization_name}")
    rich.print(f"Repo name: {session.config.repo_name}")

    # Print success message
    rich.print("\n")
    rich.print(
        Panel(
            get_success_message(*folders),
            title=f"[bold green]🚀 Codegen CLI {action} Successfully!",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    rich.print("\n")
    # Print config file location
    rich.print(
        Panel(
            f"[dim]Config file location:[/dim] [cyan]{session.codegen_dir / 'config.toml'}[/cyan]",
            title="[bold white]📝 Configuration[/bold white]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    # Print next steps panel
    rich.print("\n")
    rich.print(
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
    rich.print("\n")
