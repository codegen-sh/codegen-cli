import rich
import rich_click as click
from rich.status import Status

from codegen.analytics.decorators import track_command
from codegen.api.client import API
from codegen.api.schemas import AskExpertResponse
from codegen.auth.decorator import requires_auth, requires_init
from codegen.auth.session import CodegenSession
from codegen.errors import ServerError


def pretty_print_expert_response(response: AskExpertResponse) -> None:
    """Pretty print the expert response."""
    rich.print(response.response)


@click.command(name="expert")
@track_command()
@requires_auth
@requires_init
def expert_command(session: CodegenSession, query: str):
    """Asks a codegen expert a question."""
    status = Status("Asking expert...", spinner="dots", spinner_style="purple")
    status.start()

    try:
        response = API.ask_expert(query)
        status.stop()
        rich.print.print("✓ Response received", style="green")
        pretty_print_expert_response(response)
    except ServerError as e:
        status.stop()
        raise click.ClickException(str(e))
    finally:
        status.stop()
