import click
from pathlib import Path

from codegen.analytics.decorators import track_command
from codegen.auth.decorator import requires_auth
from codegen.auth.session import CodegenSession


def get_active_codemod() -> tuple[str, Path] | None:
    """Get the name and path of the active codemod if one exists."""
    codemods_dir = Path.cwd() / ".codegen" / "codemods"
    active_codemod_file = codemods_dir / "active_codemod.txt"

    if not active_codemod_file.exists():
        return None

    active_codemod = active_codemod_file.read_text().strip()
    codemod_path = codemods_dir / active_codemod / "run.py"

    if not codemod_path.exists():
        return None

    return active_codemod, codemod_path


@click.command(name="profile")
@track_command()
@requires_auth
def profile_command(session: CodegenSession):
    """Display information about the currently authenticated user."""
    click.echo("\n🔑 Current Profile:")
    click.echo("─" * 40)
    click.echo(f"Name:  {session.profile.name}")
    click.echo(f"Email: {session.profile.email}")
    click.echo(f"Repo:  {session.repo_name}")

    # Show active codemod if one exists
    active_codemod = get_active_codemod()
    if active_codemod:
        codemod_name, codemod_path = active_codemod
        click.echo("\n📝 Active Codemod:")
        click.echo(f"Name: {codemod_name}")
        click.echo(f"Path: {codemod_path}")

    click.echo("─" * 40 + "\n")
