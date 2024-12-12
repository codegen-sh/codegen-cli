import click
import functools


class AuthError(Exception):
    """Error raised if authed user cannot be established."""

    pass


def handle_auth_error(f):
    """Decorator to handle authentication errors gracefully."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AuthError:
            click.echo("[Error]: Not authenticated. Please run 'codegen login' first.", err=True)
            exit(1)

    return wrapper
