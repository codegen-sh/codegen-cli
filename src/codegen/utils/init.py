import shutil
from pathlib import Path

from rich.status import Status

from codegen.api.client import API
from codegen.api.schemas import SerializedExample
from codegen.auth.config import CODEGEN_DIR, CODEMODS_DIR, DOCS_DIR, EXAMPLES_DIR
from codegen.utils.formatters.examples import format_example

CODEGEN_FOLDER = Path.cwd() / CODEGEN_DIR
CODEMODS_FOLDER = Path.cwd() / CODEMODS_DIR
DOCS_FOLDER = Path.cwd() / DOCS_DIR
EXAMPLES_FOLDER = Path.cwd() / EXAMPLES_DIR

GITIGNORE_CONTENT = """
# Codegen generated directories
docs/
examples/
"""


def populate_api_docs(dest: Path, api_docs: dict[str, str], status: Status):
    """Writes all API docs to the docs folder"""
    status.update("Populating API documentation...")
    # Remove existing docs
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)

    # Populate docs
    for file, content in api_docs.items():
        dest_file = dest / file
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(content)


def populate_examples(dest: Path, examples: list[SerializedExample], status: Status):
    """Populate the examples folder with examples for the current repository."""
    status.update("Populating example codemods...")
    # Remove existing examples
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)

    for example in examples:
        dest_file = dest / f"{example.name}.py"
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        formatted = format_example(example)
        dest_file.write_text(formatted)


def initialize_codegen(status: Status, is_update: bool = False) -> tuple[Path, Path, Path, Path, Path]:
    """Initialize or update the codegen directory structure and content.

    Args:
        status: Status object for progress updates
        is_update: Whether this is an update to existing installation

    Returns:
        Tuple of (codegen_folder, codemods_folder, docs_folder, examples_folder, sample_codemod_path)

    """
    action = "Updating" if is_update else "Creating"
    status.update(f"[purple]{action} folders...")

    # Create folders if they don't exist
    CODEGEN_FOLDER.mkdir(parents=True, exist_ok=True)
    CODEMODS_FOLDER.mkdir(parents=True, exist_ok=True)
    DOCS_FOLDER.mkdir(parents=True, exist_ok=True)
    EXAMPLES_FOLDER.mkdir(parents=True, exist_ok=True)

    # Create/update .gitignore
    status.update(f"{action} .gitignore...")
    gitignore_path = CODEGEN_FOLDER / ".gitignore"
    gitignore_path.write_text(GITIGNORE_CONTENT.strip())

    # Always fetch and update docs & examples
    status.update("Fetching latest docs & examples...", spinner_style="purple")
    response = API.get_docs()
    populate_api_docs(DOCS_FOLDER, response.docs, status)
    populate_examples(EXAMPLES_FOLDER, response.examples, status)

    status.update("[bold green]Done! 🎉")

    return CODEGEN_FOLDER, CODEMODS_FOLDER, DOCS_FOLDER, EXAMPLES_FOLDER
