import json
import click
import requests
import webbrowser
import asyncio
from typing import Optional

from .config import save_token, get_token
from algoliasearch.search.client import SearchClient
from rich.console import Console
from rich.table import Table

API_ENDPOINT = "https://codegen-sh--run-sandbox-cm-on-string.modal.run"
AUTH_URL = "https://codegen.sh/login"

ALGOLIA_APP_ID = "Q48PJS245N"
ALGOLIA_SEARCH_KEY = "14f93aa799ce73ab86b93083edbeb981"
ALGOLIA_INDEX_NAME = "prod_knowledge"


class AuthError(Exception):
    pass


def get_cookies() -> dict:
    """Get cookies with auth token if it exists"""
    token = get_token()
    if not token:
        raise AuthError("Not authenticated. Please run 'codegen login' first.")
    return {"__authSession": token}


def get_auth_details() -> tuple[requests.cookies.RequestsCookieJar, dict]:
    """Get both cookies and headers with auth token"""
    token = get_token()
    if not token:
        raise AuthError("Not authenticated. Please run 'codegen login' first.")

    cookies = requests.cookies.RequestsCookieJar()
    cookies.set("__authSession", token, path="/", secure=True)

    return (
        cookies,
        {"Authorization": f"Bearer {token}"},
    )


@click.group()
def main():
    """Codegen CLI - Transform your code with AI"""
    pass


@main.command()
def login():
    """Authenticate with Codegen through the web interface"""
    click.echo(f"Opening {AUTH_URL} in your browser...")
    webbrowser.open(AUTH_URL)
    token = click.prompt("Please paste your token here", type=str)
    save_token(token)
    click.echo("Successfully authenticated!")


@main.command()
@click.argument("token")
def auth(token: str):
    """Directly save an authentication token"""
    save_token(token)
    click.echo("Successfully authenticated!")


@main.command()
@click.argument("code", required=True)
@click.option(
    "--repo-id",
    "-r",
    help="Repository ID to run the transformation on",
    required=True,
    type=int,
)
@click.option(
    "--codemod-id",
    "-c",
    help="Codemod ID to run",
    required=True,
    type=int,
)
def run(code: str, repo_id: int, codemod_id: int):
    """Run code transformation on the provided Python code"""
    try:
        cookies, headers = get_auth_details()

        # Constructing payload to match the frontend's structure
        payload = {
            "code": code,
            "repo_id": repo_id,
            "codemod_id": codemod_id,
            "codemod_source": "string",
            "source": "cli",
            "template_context": {},
            "includeGraphviz": False,
        }

        click.echo(f"Sending request to {API_ENDPOINT}")
        click.echo(f"Cookies: {cookies}")
        click.echo(f"Headers: {headers}")
        click.echo(f"Payload: {payload}")

        response = requests.post(
            API_ENDPOINT,
            cookies=cookies,
            headers=headers,
            json=payload,
        )

        if response.status_code == 200:
            result = response.json()
            # Assuming the response structure matches what we need
            if result.get("success"):
                click.echo(
                    result.get("transformed_code", "No transformed code returned")
                )
            else:
                click.echo(
                    f"Error: {result.get('error', 'Unknown error occurred')}", err=True
                )
        else:
            click.echo(f"Error: HTTP {response.status_code}", err=True)
            try:
                error_json = response.json()
                click.echo(f"Error details: {error_json}", err=True)
            except:
                click.echo(f"Raw response: {response.text}", err=True)

    except AuthError as e:
        click.echo(str(e), err=True)
        return 1
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to server: {str(e)}", err=True)
        return 1


@main.command()
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
def docs_search(query: str, page: int, hits: int):
    """Search Codegen documentation"""
    try:
        # Run the async search in the event loop
        results = asyncio.run(async_docs_search(query, page, hits))
        results = json.loads(results)
        results = results["results"][0]
        hits_list = results["hits"]

        # Print search stats
        total_hits = results.get("nbHits", 0)
        total_pages = results.get("nbPages", 0)
        click.echo(f"\nFound {total_hits} results for '{query}' ({total_pages} pages)")
        click.echo(f"Showing page {page + 1} of {total_pages}\n")

        # Print each hit with better formatting
        for i, hit in enumerate(hits_list, 1):
            click.echo("─" * 80)  # Separator line
            click.echo(f"\n[{i}] {hit['name']}")
            if hit.get("docstring"):
                click.echo("\nDescription:")
                click.echo(hit["docstring"].strip())
            if hit.get("source"):
                click.echo("\nSource:")
                click.echo("```")
                click.echo(hit["source"].strip())
                click.echo("```")
            click.echo()  # Extra newline for readability

        if hits_list:
            click.echo("─" * 80)  # Final separator

            # Navigation help
            if page > 0:
                click.echo(
                    "\nPrevious page: codegen docs-search -p {} '{}'".format(
                        page - 1, query
                    )
                )
            if page + 1 < total_pages:
                click.echo(
                    "Next page: codegen docs-search -p {} '{}'".format(page + 1, query)
                )

    except Exception as e:
        click.echo(f"Error searching docs: {str(e)}", err=True)
        return 1


async def async_docs_search(query: str, page: int, hits_per_page: int):
    """Async function to perform the actual search"""
    client = SearchClient(ALGOLIA_APP_ID, ALGOLIA_SEARCH_KEY)

    try:
        response = await client.search(
            search_method_params={
                "requests": [
                    {
                        "indexName": ALGOLIA_INDEX_NAME,
                        "query": query,
                        "hitsPerPage": hits_per_page,
                        "page": page,
                    },
                ],
            },
        )
        return response.to_json()

    finally:
        await client.close()


if __name__ == "__main__":
    main()
