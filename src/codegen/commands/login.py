import os

import click

from codegen.analytics.posthog_tracker import track_command
from codegen.auth.token_manager import TokenManager


@click.command(name="login")
@track_command()
@click.option("--token", required=False, help="JWT token for authentication")
def login_command(token: str):
    """Store authentication token."""
    _token = token
    if not _token:
        _token = os.environ.get("CODEGEN_USER_ACCESS_TOKEN")

    if not _token:
        click.echo("Error: Token must be provided via --token option or CODEGEN_USER_ACCESS_TOKEN environment variable", err=True)
        exit(1)

    token_manager = TokenManager()

    token_value = token_manager.get_token()
    if token_value:
        click.echo("Already authenticated. Use 'codegen logout' to clear the token.")
        exit(1)

    try:
        token_manager.save_token(_token)
        click.echo("Successfully stored authentication token")
    except ValueError as e:
        click.echo(f"Error: {e!s}", err=True)
        exit(1)
