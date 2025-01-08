from collections.abc import Callable
from functools import wraps
from typing import Optional, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


class Function:
    def __init__(self, name: str):
        self.name = name
        self.func: Optional[Callable] = None

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
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
        def run(codebase: PyCodebase):
            pass

    """
    return Function(name)
