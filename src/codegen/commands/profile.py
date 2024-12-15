import click

from codegen.analytics.decorators import track_command
from codegen.auth.decorator import requires_auth, requires_init
from codegen.auth.session import CodegenSession


@click.command(name="profile")
@track_command()
@requires_auth
@requires_init
def profile_command(session: CodegenSession):
    """Display information about the currently authenticated user."""
    click.echo("\n🔑 Current Profile:")
    click.echo("─" * 40)
    click.echo(f"Name:  {session.profile.name}")
    click.echo(f"Email: {session.profile.email}")
    click.echo(f"Repo:  {session.repo_name}")

    # Show active codemod if one exists
    active_codemod = session.active_codemod
    if active_codemod:
        codemod_name, codemod_path = active_codemod
        click.echo("\n📝 Active Codemod:")
        click.echo(f"Name: {codemod_name}")
        click.echo(f"Path: {codemod_path}")

    click.echo("─" * 40 + "\n")
