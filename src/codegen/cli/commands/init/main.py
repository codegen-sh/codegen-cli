import subprocess
import sys

import click
import rich
import rich_click as click
from rich import box
from rich.panel import Panel
from rich.status import Status

from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.commands.init.render import get_success_message
from codegen.cli.git.url import get_git_organization_and_repo
from codegen.cli.workspace.initialize_workspace import initialize_codegen


@click.command(name="init")
@click.option("--repo-name", type=str, help="The name of the repository")
@click.option("--organization-name", type=str, help="The name of the organization")
@requires_auth
def init_command(session: CodegenSession, repo_name: str | None = None, organization_name: str | None = None):
    """Initialize or update the Codegen folder."""
    # Print a message if not in a git repo
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        rich.print("\n")
        rich.print(
            Panel(
                "[bold red]Error:[/bold red] Not in a git repository\n\n"
                "[white]Please run this command from within a git repository.[/white]\n\n"
                "[dim]To initialize a new git repository:[/dim]\n"
                "  1. [cyan]git init[/cyan]\n"
                "  2. [cyan]git remote add origin <your-repo-url>[/cyan]\n"
                "  3. Run [cyan]codegen init[/cyan] again",
                title="[bold red]❌ Git Repository Required",
                border_style="red",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        rich.print("\n")
        sys.exit(1)

    codegen_dir = session.codegen_dir

    is_update = codegen_dir.exists()

    action = "Updating" if is_update else "Initializing"

    if organization_name is not None:
        session.config.organization_name = organization_name
    if repo_name is not None:
        session.config.repo_name = repo_name
    if not session.config.organization_name or not session.config.repo_name:
        cwd_org, cwd_repo = get_git_organization_and_repo(session.git_repo)
        session.config.organization_name = session.config.organization_name or cwd_org
        session.config.repo_name = session.config.repo_name or cwd_repo
    session.write_config()

    with Status(f"[bold]{action} Codegen...", spinner="dots", spinner_style="purple") as status:
        folders = initialize_codegen(status, is_update=is_update)
    rich.print(f"Organization name: {session.config.organization_name}")
    rich.print(f"Repo name: {session.config.repo_name}")

    config_file = session.codegen_dir / "config.toml"

    # Print success message
    rich.print("\n")
    rich.print(
        Panel(
            get_success_message(*folders, config_file),
            title=f"[bold green]🚀 Codegen CLI {action} Successfully!",
            border_style="green",
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
            "[dim]This will create a new codemod in the codegen-sh/codemods folder and initialize it with an AI-generated v0.1.[/dim]\n\n"
            "[bold white]Then run it with:[/bold white]\n\n"
            "[cyan]\tcodegen run my-codemod-name --apply-local[/cyan]\n\n"
            "[dim]This will apply your codemod and show you the results.[/dim]",
            title="[bold white]✨ What's Next?[/bold white]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    rich.print("\n")
