import time
from contextlib import contextmanager
from functools import wraps

from codegen.analytics.posthog_tracker import PostHogTracker
from codegen.analytics.utils import print_debug_message
from codegen.auth.session import CodegenSession

POSTHOG_TRACKER = PostHogTracker(CodegenSession())


def track_command():
    """Decorator to track command execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with track_command_execution(func.__name__):
                return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def track_command_execution(command_name: str):
    """Context manager to track command execution time and success."""
    start_time = time.time()
    success = True
    try:
        yield
    except BaseException:
        success = False
        raise
    finally:
        duration = time.time() - start_time
        print_debug_message(f"Command {command_name} took {duration:.2f} seconds")
        POSTHOG_TRACKER.capture_event(f"cli_command_{command_name}", {"duration": duration, "success": success, "command": command_name})
        print_debug_message(f"Command {command_name} execution tracked")
