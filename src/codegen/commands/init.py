import shutil
from pathlib import Path

import click
import requests
from rich.console import Console
from rich.status import Status

from codegen.analytics.decorators import track_command
from codegen.api.client import API
from codegen.api.schemas import SerializedExample
from codegen.auth.decorator import requires_auth
from codegen.auth.session import CodegenSession
from codegen.errors import ServerError
from codegen.utils.formatters.examples import format_example
from codegen.utils.constants import ProgrammingLanguage

###########################################################################
# STRING FORMATTING
###########################################################################


def get_success_message(codegen_folder: Path, codemods_folder: Path, docs_folder: Path, examples_folder: Path, sample_codemod_path: Path) -> str:
    return f"""
📁 Folders Created:
   • Codegen:  {codegen_folder}
   • Codemods: {codemods_folder}
   • Docs:     {docs_folder}
   • Examples: {examples_folder}

📝 Sample Codemod:
   {sample_codemod_path}

🔨 Getting Started:
   1. Add your codemods to the codemods folder
   2. Run them with: codegen run --codemod <path>
   3. Try the sample: codegen run --codemod {sample_codemod_path}

💡 Tips:
   • Use absolute paths for all arguments
   • Codemods use the graph_sitter library
   • Run 'codegen docs_search' for examples and documentation
"""


CODEGEN_FOLDER = Path.cwd() / ".codegen"
CODEMODS_FOLDER = CODEGEN_FOLDER / "codemods"
SAMPLE_CODEMOD = """
# grab codebase content
file = codebase.files[0] # or .get_file("test.py")
function = codebase.functions[0] # or .get_symbol("my_func")

# print logs
print(f'# of files: {len(codebase.files)}')
print(f'# of functions: {len(codebase.functions)}')

# make edits
file.edit('🌈' + file.content) # edit contents
function.rename('new_name') # rename
function.set_docstring('new docstring') # set docstring

# ... etc.
"""

# Add new constant for gitignore content
GITIGNORE_CONTENT = """
# Codegen generated directories
docs/
examples/
"""


###########################################################################
# POPULATE FOLDERS
###########################################################################


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
    """Populate the skills folder with skills for the current repository."""
    status.update("Populating example codemods...")
    # Remove existing examples
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)

    for example in examples:
        dest_file = dest / f"{example.name}.py"
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        formatted = format_example(example)
        dest_file.write_text(formatted)


###########################################################################
# COMMAND
###########################################################################


@click.command(name="init")
@track_command()
@requires_auth
def init_command(session: CodegenSession):
    """Initialize the Codegen folder.
    Hits up an API to do so.
    """
    console = Console()

    # Create folders
    with console.status("[bold green]Initializing Codegen...") as status:
        status.update("Creating folders...")
        CODEGEN_FOLDER.mkdir(parents=True, exist_ok=True)
        CODEMODS_FOLDER.mkdir(parents=True, exist_ok=True)
        SAMPLE_CODEMOD_PATH = CODEMODS_FOLDER / "sample_codemod.py"
        SAMPLE_CODEMOD_PATH.write_text(SAMPLE_CODEMOD)
        DOCS_FOLDER = CODEGEN_FOLDER / "docs"
        EXAMPLES_FOLDER = CODEGEN_FOLDER / "examples"  # Renamed from SKILLS_FOLDER
        DOCS_FOLDER.mkdir(parents=True, exist_ok=True)
        EXAMPLES_FOLDER.mkdir(parents=True, exist_ok=True)

        # Create .gitignore file
        status.update("Creating .gitignore...")
        gitignore_path = CODEGEN_FOLDER / ".gitignore"
        gitignore_path.write_text(GITIGNORE_CONTENT.strip())

        status.update("Fetching docs & examples...")
        response = API.get_docs()
        populate_api_docs(DOCS_FOLDER, response.docs, status)
        populate_examples(EXAMPLES_FOLDER, response.examples, status)  # Updated folder path

        status.update("Done! 🎉")

    click.echo("\n🚀 Codegen CLI Initialized Successfully!")
    click.echo("━" * 60)
    click.echo(get_success_message(CODEGEN_FOLDER, CODEMODS_FOLDER, DOCS_FOLDER, EXAMPLES_FOLDER, SAMPLE_CODEMOD_PATH))
    click.echo("━" * 60 + "\n")
