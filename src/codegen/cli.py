from dotenv import load_dotenv

from codegen.api.webapp_routes import USER_SECRETS_ROUTE

load_dotenv()

import asyncio
import json
import os
import shutil
from pathlib import Path

import click
import requests
from algoliasearch.search.client import SearchClient

from codegen.api.endpoints import DOCS_ENDPOINT, RUN_CODEMOD_ENDPOINT, SKILLS_ENDPOINT
from codegen.api.schemas import SkillOutput
from codegen.auth.token_manager import TokenManager, get_current_token
from codegen.errors import AuthError, handle_auth_error
from codegen.run.process_output import run_200_handler
from codegen.skills import format_skill
from codegen.utils.constants import ProgrammingLanguage
from tracker.tracker import PostHogTracker, track_command

API_ENDPOINT = "https://codegen-sh--run-sandbox-cm-on-string.modal.run"
AUTH_URL = "http://localhost:8000/login"


AUTH_URL = "https://codegen.sh/login"

ALGOLIA_APP_ID = "Q48PJS245N"
ALGOLIA_SEARCH_KEY = os.environ.get("ALGOLIA_SEARCH_KEY")
ALGOLIA_INDEX_NAME = "prod_knowledge"
CODEGEN_FOLDER = Path.cwd() / ".codegen"
CODEMODS_FOLDER = CODEGEN_FOLDER / "codemods"
# language=python
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

tracker = PostHogTracker()


@click.group()
def main():
    """Codegen CLI - Transform your code with AI."""
    pass


@click.group()
def cli():
    pass


@main.command()
@track_command(tracker)
@handle_auth_error
def init():
    """Initialize the codegen folder"""
    # First check authentication
    success = _init_auth()
    if not success:
        click.echo("Failed to authenticate. Please try again.")
        return

    token = get_current_token()
    # Continue with folder setup
    CODEGEN_FOLDER.mkdir(parents=True, exist_ok=True)
    CODEMODS_FOLDER.mkdir(parents=True, exist_ok=True)
    SAMPLE_CODEMOD_PATH = CODEMODS_FOLDER / "sample_codemod.py"
    SAMPLE_CODEMOD_PATH.write_text(SAMPLE_CODEMOD)
    DOCS_FOLDER = CODEGEN_FOLDER / "docs"
    SKILLS_FOLDER = CODEGEN_FOLDER / "skills"
    DOCS_FOLDER.mkdir(parents=True, exist_ok=True)

    # Only populate docs if we have authentication
    if token:
        SKILLS_FOLDER.mkdir(parents=True, exist_ok=True)
        populate_docs(DOCS_FOLDER)
        populate_skills(SKILLS_FOLDER)
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


def populate_skills(dest: Path):
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
            json={"language": language.value.upper()},
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


@main.command()
@track_command(tracker)
def logout():
    """Clear stored authentication token."""
    token_manager = TokenManager()
    token_manager.clear_token()
    click.echo("Successfully logged out")


@main.command()
@track_command(tracker)
@click.option("--token", required=False, help="JWT token for authentication")
def login(token: str):
    """Store authentication token."""
    _token = token
    if not _token:
        _token = os.environ.get("CODEGEN_USER_ACCESS_TOKEN")

    if not _token:
        click.echo("Error: Token must be provided via --token option or CODEGEN_USER_ACCESS_TOKEN environment variable", err=True)
        exit(1)

    token_manager = TokenManager()

    token_value = token_manager.get_token()
    if token_value:
        click.echo("Already authenticated. Use 'codegen logout' to clear the token.")
        exit(1)

    try:
        token_manager.save_token(_token)
        click.echo("Successfully stored authentication token")
    except ValueError as e:
        click.echo(f"Error: {e!s}", err=True)
        exit(1)


@main.command()
@track_command(tracker)
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
def run(codemod_path: Path, repo_id: int, web: bool = False):
    """Run code transformation on the provided Python code."""
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


def format_api_doc(hit: dict, index: int) -> None:
    """Format and print an API documentation entry."""
    click.echo("─" * 80)  # Separator line
    click.echo(f"\n[{index}] {hit['fullname']}")

    if hit.get("description"):
        click.echo("\nDescription:")
        click.echo(hit["description"].strip())

    # Print additional API-specific details
    click.echo("\nDetails:")
    click.echo(f"Type: {hit.get('level', 'N/A')} ({hit.get('docType', 'N/A')})")
    click.echo(f"Language: {hit.get('language', 'N/A')}")
    if hit.get("className"):
        click.echo(f"Class: {hit['className']}")
    click.echo(f"Path: {hit.get('path', 'N/A')}")
    click.echo()


def format_example(hit: dict, index: int) -> None:
    """Format and print an example entry."""
    click.echo("─" * 80)  # Separator line

    # Title with emoji if available
    title = f"\n[{index}] {hit['name']}"
    if hit.get("emoji"):
        title = f"{title} {hit['emoji']}"
    click.echo(title)

    if hit.get("docstring"):
        click.echo("\nDescription:")
        click.echo(hit["docstring"].strip())

    if hit.get("source"):
        click.echo("\nSource:")
        click.echo("```")
        click.echo(hit["source"].strip())
        click.echo("```")

    # Additional metadata
    if hit.get("language") or hit.get("user_name"):
        click.echo("\nMetadata:")
        if hit.get("language"):
            click.echo(f"Language: {hit['language']}")
        if hit.get("user_name"):
            click.echo(f"Author: {hit['user_name']}")

    click.echo()


@main.command()
@track_command(tracker)
@click.argument("query")
@click.option(
    "--page",
    "-p",
    help="Page number (starts at 0)",
    default=0,
    type=int,
)
@click.option(
    "--hits",
    "-n",
    help="Number of results per page",
    default=5,
    type=int,
)
@click.option(
    "--doctype",
    "-d",
    help="Filter by documentation type (api or example)",
    type=click.Choice(["api", "example"], case_sensitive=False),
)
def docs_search(query: str, page: int, hits: int, doctype: str | None):
    """Search Codegen documentation."""
    try:
        # Run the async search in the event loop
        results = asyncio.run(async_docs_search(query, page, hits, doctype))
        results = json.loads(results)
        results = results["results"][0]
        hits_list = results["hits"]

        # Print search stats
        total_hits = results.get("nbHits", 0)
        total_pages = results.get("nbPages", 0)
        doctype_str = f" ({doctype} only)" if doctype else ""
        click.echo(f"\nFound {total_hits} results for '{query}'{doctype_str} ({total_pages} pages)")
        click.echo(f"Showing page {page + 1} of {total_pages}\n")

        # Print each hit with appropriate formatting
        for i, hit in enumerate(hits_list, 1):
            if hit.get("type") == "doc":
                format_api_doc(hit, i)
            else:
                format_example(hit, i)

        if hits_list:
            click.echo("─" * 80)  # Final separator

            # Navigation help with doctype if specified
            doctype_param = f" -d {doctype}" if doctype else ""
            if page > 0:
                click.echo(f"\nPrevious page: codegen docs-search -p {page - 1}{doctype_param} '{query}'")
            if page + 1 < total_pages:
                click.echo(f"Next page: codegen docs-search -p {page + 1}{doctype_param} '{query}'")

    except Exception as e:
        click.echo(f"Error searching docs: {e!s}", err=True)
        return 1


async def async_docs_search(query: str, page: int, hits_per_page: int, doctype: str | None):
    """Async function to perform the actual search."""
    client = SearchClient(ALGOLIA_APP_ID, ALGOLIA_SEARCH_KEY)

    try:
        # Build the search params
        search_params = {
            "indexName": ALGOLIA_INDEX_NAME,
            "query": query,
            "hitsPerPage": hits_per_page,
            "page": page,
        }

        # Add filters based on doctype
        if doctype == "api":
            search_params["filters"] = "type:doc"
        elif doctype == "example":
            search_params["filters"] = "type:skill_implementation"

        response = await client.search(
            search_method_params={
                "requests": [search_params],
            },
        )
        return response.to_json()

    finally:
        await client.close()


if __name__ == "__main__":
    main()
