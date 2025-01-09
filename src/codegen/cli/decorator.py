from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Optional, ParamSpec, TypeVar, get_type_hints, Sequence

P = ParamSpec("P")
T = TypeVar("T")


class Function:
    def __init__(self, name: str, *, lint_mode: bool = False, lint_user_whitelist: Sequence[str] | None = None):
        self.name = name
        self.func: Optional[Callable] = None
        self.params_type = None
        self.lint_mode = lint_mode
        self.lint_user_whitelist = list(lint_user_whitelist) if lint_user_whitelist else []

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        # Get the params type from the function signature
        hints = get_type_hints(func)
        if "params" in hints:
            self.params_type = hints["params"]

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Here we'll eventually add the logic for deployment
            return func(*args, **kwargs)

        self.func = wrapper
        return wrapper


def function(name: str) -> Function:
    """Decorator for codegen functions.

    Args:
        name: The name of the function to be used when deployed

    Example:
        @codegen.function('my-function')
        def run(codebase: PyCodebase, params: MyPydanticType):
            pass
    """
    return Function(name)


def pr_check(name: str, users: Sequence[str]) -> Function:
    """Decorator for PR check functions.

    Args:
        name: The name of the function to be used when deployed
        users: List of GitHub usernames to notify (with or without @ symbol)

    Example:
        @codegen.pr_check('notify-multiple-suspense-queries', users=['@fmunir_ramp'])
        def run(codebase: Codebase, pr: PullRequest):
            pass
    """
    # Normalize usernames by removing @ if present
    normalized_users = [user.lstrip("@") for user in users]
    return Function(name, lint_mode=True, lint_user_whitelist=normalized_users)
