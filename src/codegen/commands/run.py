import json
import webbrowser
from pathlib import Path

import click
import requests
from pygit2.repository import Repository
from requests import Response
from rich.json import JSON

from codegen.analytics.decorators import track_command
from codegen.api.endpoints import RUN_CODEMOD_ENDPOINT
from codegen.api.schemas import RunCodemodInput, RunCodemodOutput
from codegen.rich.pretty_print import pretty_print_output
from codegen.utils.git.patch import apply_patch
from codegen.utils.git.repo import get_git_repo
from codegen.utils.git.url import get_repo_full_name


@click.command(name="run")
@track_command()
@click.argument("codemod_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.argument("repo_path", required=False, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--web",
    is_flag=True,
    help="Return a web link to the diff",
)
@click.option(
    "--apply-local",
    is_flag=True,
    help="Applies the generated diff to the repository",
)
def run_command(codemod_path: Path, repo_path: Path | None = None, web: bool = False, apply_local: bool = False):
    """Run code transformation on the provided Python code.

    Arguments:
        (required) codemod_path: Path to the codemod file to execute
        (optional) repo_path: Path to the repository to run the codemod on. Defaults to the current working directory.

    """
    click.echo(f"Run codemod_path={codemod_path} repo_path={repo_path} ...")

    # TODO: add back in once login works
    # auth_token = get_current_token()
    # if not auth_token:
    #     raise AuthError("Not authenticated. Please run 'codegen login' first.")

    repo_path = repo_path or Path.cwd()
    git_repo = get_git_repo(repo_path)
    if not git_repo:
        click.echo(f"400 BadRequest: No git repository found at {repo_path}")

    run_input = RunCodemodInput(
        repo_full_name=get_repo_full_name(git_repo),
        codemod_source=codemod_path.read_text(),
        web=web,
    )

    click.echo(f"Sending request to {RUN_CODEMOD_ENDPOINT} ...")
    click.echo(f"Payload: {run_input}")

    response = requests.post(
        RUN_CODEMOD_ENDPOINT,
        json=run_input.model_dump(),
    )

    if response.status_code == 200:
        run_200_handler(git_repo=git_repo, web=web, apply_local=apply_local, response=response)
    else:
        click.echo(f"{response.status_code}", err=True)
        try:
            error_json = response.json()
            click.echo(f"Details: {json.dumps(error_json, indent=4)}", err=True)
        except Exception:
            click.echo(f"Details: {response.text}", err=True)


observation = '''
diff --git a/codegen-backend/app/utils/csv_utils.py b/codegen-backend/app/utils/csv_utils.py
index 3cd4fd366f7a67a8e294ad3a4e6c6139305067d0..6f268a82218a74f652ded2ace909842f75a9ef54 100644
--- a/codegen-backend/app/utils/csv_utils.py
+++ b/codegen-backend/app/utils/csv_utils.py
@@ -1,8 +1,3 @@
-def list_to_comma_separated(items: list[str]) -> str:
-    """Given a list of items, returns a comma separated string of the items"""
-    return ",".join(items)
-
-
 def comma_separated_to_list(comma_separated: str) -> list[str]:
     """Given a comma separated string, returns a list of the comma separated items.
     Strips whitespace from each item, drops any items that are whitespace only
'''


def run_200_handler(git_repo: Repository, web: bool, apply_local: bool, response: Response):
    run_output = RunCodemodOutput.model_validate(response.json())
    if not run_output:
        click.echo(f"422 UnprocessableEntity: {JSON(response.text)}")
        return
    if not run_output.success:
        click.echo(f"500 InternalServerError: {run_output.observation}")
        return

    pretty_print_output(run_output)

    if web and run_output.web_link:
        webbrowser.open_new(run_output.web_link)

    if apply_local and run_output.observation:
        apply_patch(git_repo, f"\n{run_output.observation}\n")
        click.echo(f"Diff applied to {git_repo.path}")
