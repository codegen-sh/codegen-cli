import webbrowser
from typing import TextIO

import rich
import rich_click as click
from rich.prompt import Prompt

from codegen.api.webapp_routes import USER_SECRETS_ROUTE
from codegen.auth.session import CodegenSession
from codegen.auth.token_manager import TokenManager
from codegen.env.global_env import global_env


class UnbufferedTextIO(TextIO):
    """Unbuffered text IO that reads until newline."""

    def __init__(self):
        import sys

        self._stdin = sys.stdin

    def readline(self) -> str:
        return self._stdin.readline()

    def read(self, size: int = -1) -> str:
        if size < 0:
            return self.readline()
        return self._stdin.read(size)

    def write(self, s: str) -> int:
        import sys

        return sys.stdout.write(s)

    def flush(self) -> None:
        import sys

        sys.stdout.flush()


def login_routine() -> CodegenSession:
    """Guide user through login flow and return authenticated session.

    Args:
        console: Optional console for output. Creates new one if not provided.

    Returns:
        CodegenSession: Authenticated session

    Raises:
        click.ClickException: If login fails

    """
    # Try environment variable first
    _token = global_env.CODEGEN_USER_ACCESS_TOKEN

    # If no token in env, guide user through browser flow
    if not _token:
        rich.print(f"Opening {USER_SECRETS_ROUTE} to get your authentication token...")
        webbrowser.open_new(USER_SECRETS_ROUTE)
        _token = Prompt.ask("Please enter your authentication token from the browser", password=True, stream=UnbufferedTextIO())

    if not _token:
        raise click.ClickException("Token must be provided via CODEGEN_USER_ACCESS_TOKEN environment variable or manual input")

    # Validate and store token
    token_manager = TokenManager()
    try:
        if token_manager.validate_expiration(_token):
            token_manager.save_token(_token)
            rich.print(f"[green]✓ Stored token to:[/green] {token_manager.token_file}")
        else:
            raise click.ClickException("Token has expired. Please get a new one.")
    except ValueError as e:
        raise click.ClickException(f"Error: {e!s}")

    # Create and return new session
    return CodegenSession(_token)
