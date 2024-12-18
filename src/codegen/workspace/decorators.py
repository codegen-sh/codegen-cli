import functools
from collections.abc import Callable

import rich
from rich.status import Status

from codegen.auth.session import CodegenSession
from codegen.workspace.initialize_workspace import initialize_codegen


def requires_init(f: Callable) -> Callable:
    """Decorator that ensures codegen has been initialized."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        session: CodegenSession | None = kwargs.get("session")
        if not session:
            raise ValueError("@requires_init must be used after @requires_auth")

        if not session.codegen_dir.exists():
            rich.print("Codegen not initialized. Running init command first...")
            with Status("[bold]Initializing Codegen...", spinner="dots", spinner_style="purple") as status:
                initialize_codegen(status)

        return f(*args, **kwargs)

    return wrapper
