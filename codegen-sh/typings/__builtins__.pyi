from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.codemod.compilation.models.context import CodemodContext
    from app.codemod.compilation.models.pr_options import PROptions
    from graph_sitter import CodebaseType

# declare global type for 'codebase'
codebase: CodebaseType = None

# declare global type for 'context'
context: CodemodContext

pr_options: PROptions
