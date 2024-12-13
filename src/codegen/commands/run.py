import json
from pathlib import Path

import click
import requests

from codegen.analytics.posthog_tracker import track_command
from codegen.api.endpoints import RUN_CODEMOD_ENDPOINT
from codegen.run.process_response import run_200_handler


@click.command(name="run")
@track_command()
@click.argument("codemod_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--repo-id",
    "-r",
    help="Repository ID to run the transformation on",
    required=True,
    type=int,
)
@click.option(
    "--web",
    is_flag=True,
    help="Return a web link to the diff",
)
def run_command(codemod_path: Path, repo_id: int, web: bool = False):
    """Run code transformation on the provided Python code.

    Arguments:
        codemod_path: Path to the codemod file to execute

    """
    print(f"Run codemod_path={codemod_path} repo_id={repo_id} ...")

    # TODO: add back in once login works
    # auth_token = get_current_token()
    # if not auth_token:
    #     raise AuthError("Not authenticated. Please run 'codegen login' first.")

    # TODO: also validate the input payload
    payload = {
        "repo_id": repo_id,
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
        click.echo(f"Error: HTTP {response.status_code}", err=True)
        try:
            error_json = response.json()
            click.echo(f"Error details: {error_json}", err=True)
        except Exception:
            click.echo(f"Raw response: {response.text}", err=True)
