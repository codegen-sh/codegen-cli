import functools
from typing import Callable
from inspect import signature

from codegen.auth.session import CodegenSession
from codegen.errors import AuthError


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
