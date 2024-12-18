def convert_to_cli(input: str, language: str) -> str:
    codebase_type = "PyCodebaseType" if language.lower() == "python" else "TSCodebaseType"
    return f"""
# Type hints for injected variables
from app.codemod.compilation.models.context import CodemodContext
from app.codemod.compilation.models.pr_options import PROptions
from graph_sitter import {codebase_type}

codebase: {codebase_type}
pr_options: PROptions
context: CodemodContext

# Write your code here:
{input}
"""


def convert_to_ui(input: str) -> str:
    return input
