import functools
from collections.abc import Callable

import rich

from codegen.auth.login import login_routine
from codegen.auth.session import CodegenSession


def requires_auth(f: Callable) -> Callable:
    """Decorator that ensures a user is authenticated and injects a CodegenSession."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        session = CodegenSession()

        if not session.is_authenticated():
            rich.print("[yellow]Not authenticated. Let's get you logged in first![/yellow]\n")
            session = login_routine()

        return f(*args, session=session, **kwargs)

    return wrapper
