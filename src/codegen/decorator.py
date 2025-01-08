from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Optional, ParamSpec, TypeVar, get_type_hints

P = ParamSpec("P")
T = TypeVar("T")


class Function:
    def __init__(self, name: str):
        self.name = name
        self.func: Optional[Callable] = None
        self.params_type = None

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
