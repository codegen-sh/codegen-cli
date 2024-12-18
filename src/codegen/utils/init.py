import shutil
from pathlib import Path

import rich
from pygit2.repository import Repository
from rich.status import Status

from codegen.api.client import RestAPI
from codegen.api.schemas import SerializedExample
from codegen.auth.config import CODEGEN_DIR, CODEMODS_DIR, DOCS_DIR, EXAMPLES_DIR
from codegen.auth.session import CodegenSession
from codegen.utils.config import STATE_PATH
from codegen.utils.formatters.examples import format_example
from codegen.utils.git.repo import get_git_repo


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
    repo = get_git_repo()
    REPO_PATH = Path(repo.workdir)
    CODEGEN_FOLDER = REPO_PATH / CODEGEN_DIR
    CODEMODS_FOLDER = REPO_PATH / CODEMODS_DIR
    DOCS_FOLDER = REPO_PATH / DOCS_DIR
    EXAMPLES_FOLDER = REPO_PATH / EXAMPLES_DIR

    # Create folders if they don't exist
    CODEGEN_FOLDER.mkdir(parents=True, exist_ok=True)
    CODEMODS_FOLDER.mkdir(parents=True, exist_ok=True)
    DOCS_FOLDER.mkdir(parents=True, exist_ok=True)
    EXAMPLES_FOLDER.mkdir(parents=True, exist_ok=True)
    if not repo:
        rich.print("No git repository found. Please run this command in a git repository.")
    else:
        status.update(f"{action} .gitignore...")
        modify_gitignore(repo)

    # Always fetch and update docs & examples
    status.update("Fetching latest docs & examples...", spinner_style="purple")
    shutil.rmtree(DOCS_FOLDER, ignore_errors=True)
    shutil.rmtree(EXAMPLES_FOLDER, ignore_errors=True)
    session = CodegenSession()
    response = RestAPI(session.token).get_docs()
    populate_api_docs(DOCS_FOLDER, response.docs, status)
    populate_examples(EXAMPLES_FOLDER, response.examples, status)

    status.update("[bold green]Done! 🎉")

    return CODEGEN_FOLDER, CODEMODS_FOLDER, DOCS_FOLDER, EXAMPLES_FOLDER


def add_to_gitignore_if_not_present(gitignore: Path, line: str):
    if not gitignore.exists():
        gitignore.write_text(line)
    elif line not in gitignore.read_text():
        gitignore.write_text(gitignore.read_text() + "\n" + line)


def modify_gitignore(repo: Repository):
    gitignore_path = CODEGEN_DIR / ".gitignore"
    add_to_gitignore_if_not_present(gitignore_path, "docs")
    add_to_gitignore_if_not_present(gitignore_path, "examples")
    add_to_gitignore_if_not_present(gitignore_path, STATE_PATH)
