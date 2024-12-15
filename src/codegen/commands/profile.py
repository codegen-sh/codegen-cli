import click

from codegen.analytics.decorators import track_command
from codegen.auth.decorator import requires_auth
from codegen.auth.session import CodegenSession


@click.command(name="profile")
@track_command()
@requires_auth
def profile_command(session: CodegenSession):
    """Display information about the currently authenticated user."""
    click.echo("\n🔑 Current Authentication Profile:")
    click.echo("─" * 40)
    click.echo(f"Name:  {session.profile.name}")
    click.echo(f"Email: {session.profile.email}")
    click.echo(f"Repo:  {session.repo_name}")
    click.echo("─" * 40 + "\n")
