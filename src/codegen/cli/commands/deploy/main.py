import ast
from pathlib import Path

import rich
import rich_click as click
from rich.panel import Panel
from rich.table import Table

from codegen.cli.analytics.decorators import track_command
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
                self.functions.append({"name": func_name, "line": node.lineno, "function": node.name})


@click.command(name="deploy")
@track_command()
@click.argument("filepath", type=click.Path(exists=True, path_type=Path))
def deploy_command(filepath: Path):
    """Deploy codegen functions found in the specified file."""

    # Read and parse the file
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read())
    except Exception as e:
        raise click.ClickException(f"Failed to parse {filepath}: {str(e)}")

    # Find all codegen.function decorators
    visitor = CodegenFunctionVisitor()
    visitor.visit(tree)

    if not visitor.functions:
        rich.print("\n[yellow]No @codegen.function decorators found in this file.[/yellow]\n")
        return

    # Create a table to display the results
    table = Table(title=f"Found {len(visitor.functions)} codegen function(s)")
    table.add_column("Function Name", style="cyan")
    table.add_column("Decorator Name", style="green")
    table.add_column("Line", style="magenta")

    for func in visitor.functions:
        table.add_row(func["function"], func["name"], str(func["line"]))

    rich.print("\n")
    rich.print(Panel(table, title="[bold blue]Codegen Functions", border_style="blue", padding=(1, 2)))
    rich.print("\n")
