import rich
import rich_click as click
from rich.status import Status

from codegen.analytics.decorators import track_command
from codegen.api.client import RestAPI
from codegen.auth.decorators import requires_auth
from codegen.auth.session import CodegenSession
from codegen.errors import ServerError
from codegen.workspace.decorators import requires_init


@click.command(name="expert")
@click.option("--query", "-q", help="The question to ask the expert.")
@track_command()
@requires_auth
@requires_init
def expert_command(session: CodegenSession, query: str):
    """Asks a codegen expert a question."""
    status = Status("Asking expert...", spinner="dots", spinner_style="purple")
    status.start()

    try:
        response = RestAPI(session.token).ask_expert(query)
        status.stop()
        rich.print("[bold green]✓ Response received[/bold green]")
        rich.print(response.response)
    except ServerError as e:
        status.stop()
        raise click.ClickException(str(e))
    finally:
        status.stop()