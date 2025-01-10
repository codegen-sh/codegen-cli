import ast
import textwrap
import time
from pathlib import Path

import rich
import rich_click as click

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.url import generate_webapp_url


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
                and len(decorator.args) >= 1
                and (
                    # Check if it's a direct codegen.X call
                    (isinstance(decorator.func, ast.Attribute) and isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == "codegen")
                    or
                    # Check if it starts with codegen.anything.anything...
                    (isinstance(decorator.func, ast.Attribute) and isinstance(decorator.func.value, ast.Attribute) and self._has_codegen_root(decorator.func.value))
                )
            ):
                # Get the function name from the decorator argument
                func_name = ast.literal_eval(decorator.args[0])

                # Get additional metadata for webhook
                lint_mode = any(attr == "webhook" for attr in self._get_decorator_attrs(decorator))
                lint_user_whitelist = []
                if lint_mode and len(decorator.keywords) > 0:
                    for keyword in decorator.keywords:
                        if keyword.arg == "users" and isinstance(keyword.value, ast.List):
                            lint_user_whitelist = [ast.literal_eval(elt).lstrip("@") for elt in keyword.value.elts]

                # Get just the function body, unindented
                body_source = self.get_function_body(node)
                self.functions.append({"name": func_name, "source": body_source, "lint_mode": lint_mode, "lint_user_whitelist": lint_user_whitelist})

    def _has_codegen_root(self, node):
        """Recursively check if an AST node chain starts with codegen."""
        if isinstance(node, ast.Name):
            return node.id == "codegen"
        elif isinstance(node, ast.Attribute):
            return self._has_codegen_root(node.value)
        return False

    def _get_decorator_attrs(self, node):
        """Get all attribute names in a decorator chain."""
        attrs = []
        while isinstance(node, ast.Attribute):
            attrs.append(node.attr)
            node = node.value
        return attrs

    def visit_Module(self, node):
        # Store the full source code for later use
        self.source = self.file_content
        self.generic_visit(node)


@click.command(name="deploy")
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
        raise click.ClickException(f"Failed to parse {filepath}: {e!s}")

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
        with create_spinner(f"Deploying function '{func['name']}'...") as status:
            start_time = time.time()
            response = api_client.deploy(
                codemod_name=func["name"],
                codemod_source=func["source"],
                lint_mode=func["lint_mode"],
                lint_user_whitelist=func["lint_user_whitelist"],
            )
            deploy_time = time.time() - start_time

        func_type = "Webhook" if func["lint_mode"] else "Function"
        rich.print(f"✅ {func_type} '{func['name']}' deployed in {deploy_time:.3f}s! 🎉")
        url = generate_webapp_url(path=f"functions/{response.codemod_id}")
        rich.print(f"  → view deployment: {url}\n")
