import time
from pathlib import Path

import rich
import rich_click as click

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.codemod_manager import CodemodManager
from codegen.cli.utils.function_finder import DecoratedFunction
from codegen.cli.utils.url import generate_webapp_url


def deploy_functions(session: CodegenSession, functions: list[DecoratedFunction]) -> None:
    """Deploy a list of functions."""
    if not functions:
        rich.print("\n[yellow]No @codegen.function decorators found.[/yellow]\n")
        return

    # Deploy each function
    api_client = RestAPI(session.token)
    rich.print()  # Add a blank line before deployments

    for func in functions:
        with create_spinner(f"Deploying function '{func.name}'...") as status:
            start_time = time.time()
            response = api_client.deploy(
                codemod_name=func.name,
                codemod_source=func.source,
                lint_mode=func.lint_mode,
                lint_user_whitelist=func.lint_user_whitelist,
            )
            deploy_time = time.time() - start_time

        func_type = "Webhook" if func.lint_mode else "Function"
        rich.print(f"✅ {func_type} '{func.name}' deployed in {deploy_time:.3f}s! 🎉")
        url = generate_webapp_url(path=f"functions/{response.codemod_id}")
        rich.print(f"  → view deployment: {url}\n")


@click.command(name="deploy")
@requires_auth
@click.option("-p", "--path", type=click.Path(exists=True, path_type=Path), help="Path to file or directory to deploy functions from")
@click.option("-l", "--label", help="Label of specific function to deploy")
def deploy_command(session: CodegenSession, path: Path | None = None, label: str | None = None):
    """Deploy codegen functions.

    Either specify a path to deploy all functions in that location,
    or specify a label to deploy a specific function by name.
    """
    if path and label:
        raise click.ClickException("Cannot specify both --path and --label")

    if not path and not label:
        # Default to current directory if neither is specified
        path = Path.cwd()

    try:
        if path:
            # Deploy all functions in the path
            functions = CodemodManager.get_decorated(path)
            deploy_functions(session, functions)
        else:
            # Find and deploy specific function by label
            functions = CodemodManager.get_decorated()
            matching = [f for f in functions if f.name == label]
            if not matching:
                raise click.ClickException(f"No function found with label '{label}'")
            if len(matching) > 1:
                # If multiple matches, show their locations
                rich.print(f"[yellow]Multiple functions found with label '{label}':[/yellow]")
                for func in matching:
                    rich.print(f"  • {func.filepath}")
                raise click.ClickException("Please specify the exact file with --path")
            deploy_functions(session, matching)
    except Exception as e:
        raise click.ClickException(f"Failed to deploy: {e!s}")
