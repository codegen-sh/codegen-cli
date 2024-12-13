import click

from codegen.analytics.decorators import track_command
from codegen.auth.token_manager import TokenManager


@click.command(name="logout")
@track_command()
def logout_command():
    """Clear stored authentication token."""
    token_manager = TokenManager()
    token_manager.clear_token()
    click.echo("Successfully logged out")
