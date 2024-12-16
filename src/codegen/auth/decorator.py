import functools
from collections.abc import Callable

import click
from rich.console import Console
from rich.status import Status

from codegen.auth.login import login_routine
from codegen.auth.session import CodegenSession
from codegen.errors import AuthError
from codegen.utils.init import initialize_codegen


def requires_auth(f: Callable) -> Callable:
    """Decorator that ensures a user is authenticated and injects a CodegenSession."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        session = CodegenSession()

        if not session.is_authenticated():
            console = Console()
            console.print("[yellow]Not authenticated. Let's get you logged in first![/yellow]\n")
            session = login_routine(console)

        return f(*args, session=session, **kwargs)

    return wrapper


def requires_init(f: Callable) -> Callable:
    """Decorator that ensures codegen has been initialized."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        session: CodegenSession | None = kwargs.get("session")
        if not session:
            raise ValueError("@requires_init must be used after @requires_auth")

        if not session.codegen_dir.exists():
            click.echo("Codegen not initialized. Running init command first...")
            with Status("[bold]Initializing Codegen...", spinner="dots", spinner_style="purple") as status:
                initialize_codegen(status)

        return f(*args, **kwargs)

    return wrapper
