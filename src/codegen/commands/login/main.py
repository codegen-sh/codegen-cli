import rich
import rich_click as click

from codegen.analytics.decorators import track_command
from codegen.auth.login import login_routine
from codegen.auth.session import CodegenSession
from codegen.auth.token_manager import TokenManager


@click.command(name="login")
@track_command()
@click.option("--token", required=False, help="API token for authentication")
def login_command(token: str):
    """Store authentication token."""
    # Check if already authenticated
    token_manager = TokenManager()
    if token_manager.get_token():
        raise click.ClickException("Already authenticated. Use 'codegen logout' to clear the token.")

    # Use provided token or go through login flow
    if token:
        session = CodegenSession()
        try:
            session.assert_authenticated()
            token_manager.save_token(token)
            rich.print(f"[green]✓ Stored token to:[/green] {token_manager.token_file}")
            rich.print("[cyan]📊 Hey![/cyan] We collect anonymous usage data to improve your experience 🔒")
            rich.print("To opt out, set [green]telemetry_enabled = false[/green] in [cyan]~/.config/codegen-sh/analytics.json[/cyan] ✨")
        except ValueError as e:
            raise click.ClickException(f"Error: {e!s}")
    else:
        login_routine(token)
