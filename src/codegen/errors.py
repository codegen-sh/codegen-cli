import functools

import rich_click as click
from rich.console import Console
from rich.panel import Panel

console = Console(highlight=False)


class AuthError(Exception):
    """Error raised if authed user cannot be established."""

    pass


class CodegenError(Exception):
    """Base class for Codegen-specific errors."""

    pass


class ServerError(CodegenError):
    """Error raised when the server encounters an error."""

    pass


def format_error_message(error):
    """Format error message based on error type."""
    if isinstance(error, AuthError):
        return "[red]Authentication Error:[/red] Please run 'codegen login' first."
    elif isinstance(error, ServerError):
        return "[red]Server Error:[/red] The server encountered an error. Please try again later."
    else:
        return f"[red]Error:[/red] {error!s}"


def handle_auth_error(f):
    """Decorator to handle authentication errors gracefully."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AuthError:
            console.print(Panel("[red]Authentication Error:[/red] Please run 'codegen login' first.", title="Codegen Error", border_style="red"))
            raise click.Abort()

    return wrapper


def handle_errors(cmd):
    """Global error handler for CLI commands."""

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                console.print(Panel(format_error_message(e), title="Codegen Error", border_style="red"))
                raise click.Abort()

        return wrapper

    # Apply the error handling wrapper while preserving Click command attributes
    cmd.callback = decorator(cmd.callback)
    return cmd
