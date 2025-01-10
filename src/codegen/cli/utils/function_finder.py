import ast
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DecoratedFunction:
    """Represents a function decorated with @codegen."""

    name: str
    source: str
    lint_mode: bool
    lint_user_whitelist: list[str]
    filepath: Path | None = None


class CodegenFunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions: list[DecoratedFunction] = []

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
                lint_mode = decorator.func.attr == "webhook"
                lint_user_whitelist = []
                if lint_mode and len(decorator.keywords) > 0:
                    for keyword in decorator.keywords:
                        if keyword.arg == "users" and isinstance(keyword.value, ast.List):
                            lint_user_whitelist = [ast.literal_eval(elt).lstrip("@") for elt in keyword.value.elts]

                # Get just the function body, unindented
                body_source = self.get_function_body(node)
                self.functions.append(DecoratedFunction(name=func_name, source=body_source, lint_mode=lint_mode, lint_user_whitelist=lint_user_whitelist))

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


def find_codegen_functions(filepath: Path) -> list[DecoratedFunction]:
    """Find all codegen functions in a Python file.

    Args:
        filepath: Path to the Python file to search

    Returns:
        List of DecoratedFunction objects found in the file

    Raises:
        Exception: If the file cannot be parsed

    """
    # Read and parse the file
    with open(filepath) as f:
        file_content = f.read()
        tree = ast.parse(file_content)

    # Find all codegen.function decorators
    visitor = CodegenFunctionVisitor()
    visitor.file_content = file_content
    visitor.visit(tree)

    # Add filepath to each function
    for func in visitor.functions:
        func.filepath = filepath

    return visitor.functions
