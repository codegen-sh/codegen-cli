import shutil
from pathlib import Path

import click
import requests

from codegen.analytics.decorators import track_command
from codegen.api.endpoints import DOCS_ENDPOINT, SKILLS_ENDPOINT
from codegen.api.schemas import SkillOutput
from codegen.api.webapp_routes import USER_SECRETS_ROUTE
from codegen.auth.token_manager import TokenManager, get_current_token
from codegen.errors import AuthError, handle_auth_error
from codegen.skills import format_skill
from codegen.utils.constants import ProgrammingLanguage
from codegen.utils.git.repo import get_git_repo
from codegen.utils.git.url import get_git_organization_and_repo

SAMPLE_CODEMOD = """
# grab codebase content
file = codebase.files[0] # or .get_file("test.py")
function = codebase.functions[0] # or .get_symbol("my_func")

# print logs
print(f'# of files: {len(codebase.files)}')
print(f'# of functions: {len(codebase.functions)}')

# make edits
file.edit('🌈' + file.content) # edit contents
function.rename('new_name') # rename
function.set_docstring('new docstring') # set docstring

# ... etc.

"""


@click.command(name="init")
@track_command()
@click.option("--repo-name", type=str, help="The name of the repository")
@click.option("--organization-name", type=str, help="The name of the organization")
@handle_auth_error
def init_command(repo_name: str | None = None, organization_name: str | None = None):
    """Initialize the codegen folder"""
    # First check authentication
    success = _init_auth()
    if not success:
        click.echo("Failed to authenticate. Please try again.")
        return

    token = get_current_token()
    # Continue with folder setup
    repo = get_git_repo()
    if not repo:
        click.echo("No git repository found. Please run this command in a git repository.")
        return
    REPO_PATH = Path(repo.path)
    CODEGEN_FOLDER = REPO_PATH / ".codegen"
    CODEMODS_FOLDER = CODEGEN_FOLDER / "codemods"
    CODEGEN_FOLDER.mkdir(parents=True, exist_ok=True)
    CODEMODS_FOLDER.mkdir(parents=True, exist_ok=True)
    SAMPLE_CODEMOD_PATH = CODEMODS_FOLDER / "sample_codemod.py"
    SAMPLE_CODEMOD_PATH.write_text(SAMPLE_CODEMOD)
    DOCS_FOLDER = CODEGEN_FOLDER / "docs"
    SKILLS_FOLDER = CODEGEN_FOLDER / "skills"
    DOCS_FOLDER.mkdir(parents=True, exist_ok=True)
    if not organization_name or not repo_name:
        cwd_org, cwd_repo = get_git_organization_and_repo(repo)
        organization_name = organization_name or cwd_org
        repo_name = repo_name or cwd_repo
    click.echo(f"Organization name: {organization_name}")
    click.echo(f"Repo name: {repo_name}")
    if not organization_name or not repo_name:
        click.echo("No git remote found. Please run this command in a git repository.")
        return

    # Only populate docs if we have authentication
    if token:
        SKILLS_FOLDER.mkdir(parents=True, exist_ok=True)
        populate_docs(DOCS_FOLDER)
        populate_skills(SKILLS_FOLDER, organization_name, repo_name)
        click.echo(
            "\n".join(
                [
                    "Initialized codegen-cli",
                    f"codegen_folder: {CODEGEN_FOLDER}",
                    f"codemods_folder: {CODEMODS_FOLDER}",
                    f"docs_folder: {DOCS_FOLDER}",
                    f"skills_folder: {SKILLS_FOLDER}",
                    f"sample_codemod: {SAMPLE_CODEMOD_PATH}",
                    "Please add your codemods to the codemods folder and run codegen run to run them. See the sample codemod for an example.",
                    f"You can run the sample codemod with codegen run --codemod {SAMPLE_CODEMOD_PATH}.",
                    "Please use absolute path for all arguments.",
                    "Codemods are written in python using the graph_sitter library. Use the docs_search command to find examples and documentation.",
                ]
            ),
        )
    else:
        click.echo("Skipping docs population - authentication required")


def _init_auth():
    token_manager = TokenManager()
    token = token_manager.get_token()
    if not token:
        click.echo("No authentication token found.")
        if click.confirm("Would you like to authenticate now?"):
            click.echo(f"You can find your authentication token at {USER_SECRETS_ROUTE}")

            token = click.prompt("Please enter your authentication token", type=str)
            try:
                token_manager.save_token(token)
                click.echo("Successfully stored authentication token")
            except ValueError as e:
                click.echo(f"Error saving token: {e!s}", err=True)
                return False
        else:
            click.echo("Skipping authentication. Some features may be limited.")
            return False
    return True


def populate_docs(dest: Path):
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    auth_token = get_current_token()
    if not auth_token:
        raise AuthError("Not authenticated. Please run 'codegen login' first.")
    click.echo(f"Sending request to {DOCS_ENDPOINT}")
    response = requests.get(
        DOCS_ENDPOINT,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    if response.status_code == 200:
        click.echo("Successfully fetched docs")
        for file, content in response.json().items():
            dest_file = dest / file
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            dest_file.write_text(content)
    else:
        click.echo(f"Error: HTTP {response.status_code}", err=True)
        try:
            error_json = response.json()
            click.echo(f"Error details: {error_json}", err=True)
        except Exception:
            click.echo(f"Raw response: {response.text}", err=True)


def populate_skills(dest: Path, organization_name: str, repo_name: str):
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    auth_token = get_current_token()
    if not auth_token:
        raise AuthError("Not authenticated. Please run 'codegen login' first.")
    for language in [ProgrammingLanguage.PYTHON, ProgrammingLanguage.TYPESCRIPT]:
        click.echo(f"Sending request to {SKILLS_ENDPOINT}")
        response = requests.post(
            SKILLS_ENDPOINT,
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "language": language.value.upper(),
                "organization_name": organization_name,
                "repo_name": repo_name,
            },
        )

        if response.status_code == 200:
            for skill in response.json():
                model = SkillOutput(**skill)
                dest_file = dest / language.value / f"{model.name}.py"
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                formatted_skill = format_skill(model)
                dest_file.write_text(formatted_skill)
        else:
            click.echo(f"Error: HTTP {response.status_code}", err=True)
            try:
                error_json = response.json()
                click.echo(f"Error details: {error_json}", err=True)
            except Exception:
                click.echo(f"Raw response: {response.text}", err=True)
