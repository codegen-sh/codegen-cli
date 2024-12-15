import functools
from collections.abc import Callable
from pathlib import Path

import click

from codegen.auth.session import CodegenSession
from codegen.errors import AuthError
from codegen.utils.init import initialize_codegen
from rich.status import Status


def requires_auth(f: Callable) -> Callable:
    """Decorator that ensures a user is authenticated and injects a CodegenSession.

    The decorated function must accept a 'session' parameter of type CodegenSession.

    Usage:
        @click.command()
        @requires_auth
        def protected_command(session: CodegenSession):
            click.echo(f"Hello {session.profile.name}!")
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            session = CodegenSession()
            # Inject session into the kwargs
            return f(*args, session=session, **kwargs)
        except ValueError as e:
            raise AuthError("Not authenticated. Please run 'codegen login' first.") from e

    return wrapper


def requires_init(f: Callable) -> Callable:
    """Decorator that ensures codegen has been initialized."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        session = kwargs.get("session")
        if not session:
            raise ValueError("@requires_init must be used after @requires_auth")

        codegen_dir = Path.cwd() / ".codegen"
        if not codegen_dir.exists():
            click.echo("Codegen not initialized. Running init command first...")
            with Status("[bold]Initializing Codegen...", spinner="dots", spinner_style="purple") as status:
                initialize_codegen(status)

        return f(*args, **kwargs)

    return wrapper
