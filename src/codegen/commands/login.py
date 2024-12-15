import click

from codegen.analytics.decorators import track_command
from codegen.auth.token_manager import TokenManager
from codegen.env.global_env import global_env


@click.command(name="login")
@track_command()
@click.option("--token", required=False, help="JWT token for authentication")
def login_command(token: str):
    """Store authentication token."""
    _token = token
    if not _token:
        _token = global_env.CODEGEN_USER_ACCESS_TOKEN

    if not _token:
        click.echo("Please enter your authentication token:")
        _token = input().strip().replace("\n", "").replace("\r", "")

    if not _token:
        click.echo("Error: Token must be provided via --token option, CODEGEN_USER_ACCESS_TOKEN environment variable, or manual input", err=True)
        exit(1)

    token_manager = TokenManager()

    token_value = token_manager.get_token()
    if token_value:
        click.echo("Already authenticated. Use 'codegen logout' to clear the token.")
        exit(1)

    try:
        if token_manager.validate_expiration(_token):
            token_manager.save_token(_token)
            click.echo(f"✅ Stored token to: {token_manager.token_file}")
        else:
            click.echo("Error: Token has expired. Please re-authenticate.")
            exit(1)
    except ValueError as e:
        click.echo(f"Error: {e!s}", err=True)
        exit(1)
