import ast
from pathlib import Path

import rich
import rich_click as click
from rich import box
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from codegen.cli.analytics.decorators import track_command
from codegen.cli.api.client import RestAPI
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.decorator import Function


class CodegenFunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

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
                # Get the full source code of the function
                source_lines = []
                for node_field in ast.iter_fields(node):
                    if isinstance(node_field[1], list) and all(isinstance(x, ast.stmt) for x in node_field[1]):
                        source_lines.extend(ast.get_source_segment(self.source, x) for x in node_field[1])

                self.functions.append({"name": func_name, "line": node.lineno, "function": node.name, "source": ast.get_source_segment(self.source, node)})

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

    # Create a table to display the results
    table = Table(title=f"Found {len(visitor.functions)} codegen function(s)")
    table.add_column("Function Name", style="cyan")
    table.add_column("Decorator Name", style="green")
    table.add_column("Line", style="magenta")
    table.add_column("Status", style="blue")

    rich.print("\n")
    rich.print(Panel(table, title="[bold blue]Codegen Functions", border_style="blue", padding=(1, 2)))

    # Deploy each function
    api_client = RestAPI(session.token)
    for func in visitor.functions:
        response = api_client.deploy(codemod_name=func["name"], codemod_source=func["source"])
        print(response)

    rich.print("\n[bold green]✨ Deployment complete![/bold green]\n")
