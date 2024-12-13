import asyncio
import json
import os

import click
from algoliasearch.search.client import SearchClient

from codegen.analytics.tracker import track_command

ALGOLIA_APP_ID = "Q48PJS245N"
ALGOLIA_SEARCH_KEY = os.environ.get("ALGOLIA_SEARCH_KEY")
ALGOLIA_INDEX_NAME = "prod_knowledge"


@click.command(name="docs-search")
@track_command()
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
def docs_search_command(query: str, page: int, hits: int, doctype: str | None):
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
