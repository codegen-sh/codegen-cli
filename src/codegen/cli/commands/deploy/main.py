import ast
import textwrap
from pathlib import Path
import time

import rich
import rich_click as click
from rich.status import Status

from codegen.cli.analytics.decorators import track_command
from codegen.cli.api.client import RestAPI
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession


class CodegenFunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

    def get_function_body(self, node: ast.FunctionDef) -> str:
        """Extract and unindent the function body."""
        # Get the source lines for all body nodes
        body_source = []
        for stmt in node.body:
            source = ast.get_source_segment(self.source, stmt)
            if source:
                body_source.append(source)

        # Join the lines and dedent
        body = "\n".join(body_source)
        return textwrap.dedent(body)

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and isinstance(decorator.func.value, ast.Name)
                and decorator.func.value.id == "codegen"
                and decorator.func.attr == "function"
                and len(decorator.args) >= 1
            ):
                # Get the function name from the decorator argument
                func_name = ast.literal_eval(decorator.args[0])
                # Get just the function body, unindented
                body_source = self.get_function_body(node)
                self.functions.append({"name": func_name, "source": body_source})

    def visit_Module(self, node):
        # Store the full source code for later use
        self.source = self.file_content
        self.generic_visit(node)


@click.command(name="deploy")
@track_command()
@requires_auth
@click.argument("filepath", type=click.Path(exists=True, path_type=Path))
def deploy_command(session: CodegenSession, filepath: Path):
    """Deploy codegen functions found in the specified file."""

    # Read and parse the file
    try:
        with open(filepath) as f:
            file_content = f.read()
            tree = ast.parse(file_content)
    except Exception as e:
        raise click.ClickException(f"Failed to parse {filepath}: {str(e)}")

    # Find all codegen.function decorators
    visitor = CodegenFunctionVisitor()
    visitor.file_content = file_content
    visitor.visit(tree)

    if not visitor.functions:
        rich.print("\n[yellow]No @codegen.function decorators found in this file.[/yellow]\n")
        return

    # Deploy each function
    api_client = RestAPI(session.token)
    rich.print()  # Add a blank line before deployments

    for func in visitor.functions:
        with Status(f"[bold]Deploying function '{func['name']}'...", spinner="dots") as status:
            start_time = time.time()
            response = api_client.deploy(codemod_name=func["name"], codemod_source=func["source"])
            deploy_time = time.time() - start_time

        rich.print(f"[green]✓[/green] Function '{func['name']}' deployed in {deploy_time:.3f}s! 🎉")
        rich.print(f"View Deployment: {response.url}\n")
