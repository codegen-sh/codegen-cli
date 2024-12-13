import json
from pathlib import Path

import click
import requests
from requests import Response
from rich.json import JSON

from codegen.analytics.decorators import track_command
from codegen.api.endpoints import RUN_CODEMOD_ENDPOINT
from codegen.api.schemas import RunCodemodOutput
from codegen.rich.pretty_print import pretty_print_output
from codegen.utils.git.repo import get_git_repo
from codegen.utils.git.url import get_repo_full_name


@click.command(name="run")
@track_command()
@click.argument("codemod_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.argument("repo_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--web",
    is_flag=True,
    help="Return a web link to the diff",
)
def run_command(codemod_path: Path, repo_path: Path, web: bool = False):
    """Run code transformation on the provided Python code.

    Arguments:
        codemod_path: Path to the codemod file to execute

    """
    click.echo(f"Run codemod_path={codemod_path} repo_path={repo_path} ...")

    # TODO: add back in once login works
    # auth_token = get_current_token()
    # if not auth_token:
    #     raise AuthError("Not authenticated. Please run 'codegen login' first.")

    # TODO: also create an input schema
    git_repo = get_git_repo(repo_path)
    if not git_repo:
        click.echo(f"400 BadRequest: No git repository found at {repo_path}")

    payload = {
        "repo_full_name": get_repo_full_name(git_repo),
        "codemod_source": codemod_path.read_text(),
        "web": web,
    }

    print(f"Sending request to {RUN_CODEMOD_ENDPOINT} ...")
    print(f"Payload: {json.dumps(payload, indent=4)}")

    response = requests.post(
        RUN_CODEMOD_ENDPOINT,
        json=payload,
    )

    if response.status_code == 200:
        run_200_handler(payload, response)
    else:
        click.echo(f"{response.status_code}", err=True)
        try:
            error_json = response.json()
            click.echo(f"Details: {json.dumps(error_json, indent=4)}", err=True)
        except Exception:
            click.echo(f"Details: {response.text}", err=True)


def run_200_handler(payload: dict, response: Response):
    run_output = RunCodemodOutput.model_validate(response.json())
    if not run_output:
        click.echo(f"422 UnprocessableEntity: {JSON(response.text)}")
        return
    if not run_output.success:
        click.echo(f"500 InternalServerError: {run_output.observation}")
        return
    if payload.get("web"):
        # TODO: also open in the browser
        click.echo(run_output.web_link)
        return

    pretty_print_output(run_output)
