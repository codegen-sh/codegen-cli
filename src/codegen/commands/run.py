import webbrowser
from pathlib import Path

import click
import requests
from requests import Response

from codegen.analytics.decorators import track_command
from codegen.api.endpoints import RUN_CODEMOD_ENDPOINT
from codegen.api.schemas import RunCodemodInput, RunCodemodOutput
from codegen.errors import ServerError
from codegen.rich.pretty_print import pretty_print_output
from codegen.utils.git.repo import get_git_repo
from codegen.utils.git.url import get_repo_full_name
from codegen.auth.decorator import requires_auth
from codegen.auth.session import CodegenSession


@click.command(name="run")
@track_command()
@requires_auth
@click.argument("codemod_path", required=False, type=click.Path(exists=True, path_type=Path))
@click.argument("repo_path", required=False, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--web",
    is_flag=True,
    help="Return a web link to the diff",
)
def run_command(session: CodegenSession, codemod_path: Path | None = None, repo_path: Path | None = None, web: bool = False):
    """Run code transformation on the provided Python code.

    Arguments:
        (optional) codemod_path: Path to the codemod file to execute. If not provided, uses the active codemod.
        (optional) repo_path: Path to the repository to run the codemod on. Defaults to the current working directory.

    """
    if not codemod_path:
        # Try to get active codemod
        codemods_dir = Path.cwd() / ".codegen" / "codemods"
        active_codemod_file = codemods_dir / "active_codemod.txt"

        if not active_codemod_file.exists():
            raise click.ClickException("No codemod path provided and no active codemod found.\n" "Either provide a codemod path or create one with: codegen create <name>")

        active_codemod = active_codemod_file.read_text().strip()
        codemod_path = codemods_dir / active_codemod / "run.py"

        if not codemod_path.exists():
            raise click.ClickException(f"Active codemod not found at: {codemod_path}")

    repo_path = repo_path or Path.cwd()
    git_repo = get_git_repo(repo_path)
    if not git_repo:
        raise click.BadParameter(f"No git repository found at {repo_path}")

    run_input = RunCodemodInput(
        repo_full_name=get_repo_full_name(git_repo),
        codemod_source=codemod_path.read_text(),
        web=web,
    )

    click.echo(f"Running codemod from {codemod_path} on {repo_path}...")

    try:
        response = requests.post(
            RUN_CODEMOD_ENDPOINT,
            json=run_input.model_dump(),
        )

        if response.status_code == 200:
            run_200_handler(run_input, response)
        elif response.status_code == 500:
            raise ServerError("The server encountered an error while processing your request")
        else:
            error_msg = "Unknown error occurred"
            try:
                error_json = response.json()
                error_msg = error_json.get("detail", error_json)
            except Exception:
                error_msg = response.text
            raise click.ClickException(f"Error ({response.status_code}): {error_msg}")

    except requests.RequestException as e:
        raise click.ClickException(f"Network error: {e!s}")


def run_200_handler(run_input: RunCodemodInput, response: Response):
    try:
        run_output = RunCodemodOutput.model_validate(response.json())
        if not run_output:
            raise click.ClickException("Server returned invalid response format")
        if not run_output.success:
            raise ServerError(run_output.observation or "Unknown server error occurred")

        if run_input.web and run_output.web_link:
            webbrowser.open_new(run_output.web_link)

        pretty_print_output(run_output)

    except ValueError as e:
        raise click.ClickException(f"Failed to process server response: {e!s}")
