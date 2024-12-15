import shutil
from pathlib import Path

import click
import requests

from codegen.analytics.decorators import track_command
from codegen.api.endpoints import DOCS_ENDPOINT
from codegen.api.schemas import SkillOutput
from codegen.api.webapp_routes import USER_SECRETS_ROUTE
from codegen.auth.token_manager import TokenManager, get_current_token
from codegen.errors import AuthError, handle_auth_error
from codegen.skills import format_skill
from codegen.utils.constants import ProgrammingLanguage
from codegen.utils.git.repo import get_git_repo
from codegen.utils.git.url import get_repo_full_name
from codegen.auth.decorator import requires_auth
from codegen.auth.session import CodegenSession
from codegen.errors import ServerError

###########################################################################
# STRING FORMATTING
###########################################################################


def get_success_message(codegen_folder: Path, codemods_folder: Path, docs_folder: Path, skills_folder: Path, sample_codemod_path: Path) -> str:
    return f"""
📁 Folders Created:
   • Codegen:  {codegen_folder}
   • Codemods: {codemods_folder}
   • Docs:     {docs_folder}
   • Skills:   {skills_folder}

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


###########################################################################
# FETCH ROUTINES
###########################################################################


def fetch_docs(session: CodegenSession) -> dict[str, str]:
    response = requests.get(
        DOCS_ENDPOINT,
        headers={"Authorization": f"Bearer {session.token}"},
        json={"repo_full_name": session.repo_name, "language": ProgrammingLanguage.PYTHON.value.upper()},
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise ServerError(f"Error: HTTP {response.status_code}")


def populate_api_docs(dest: Path, api_docs: dict[str, str]):
    """Writes all API docs to the docs folder"""
    # Remove existing docs
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)

    # Populate docs
    for file, content in api_docs.items():
        dest_file = dest / file
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(content)


def populate_examples(dest: Path, examples: list[dict]):
    """Populate the skills folder with skills for the current repository."""
    # Remove existing examples
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)

    for example in examples:
        model = SkillOutput(**example)
        dest_file = dest / f"{model.name}.py"
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        formatted_skill = format_skill(model)
        dest_file.write_text(formatted_skill)


###########################################################################
# COMMAND
###########################################################################


@click.command(name="init")
@track_command()
@requires_auth
def init_command(session: CodegenSession):
    """
    Initialize the Codegen folder.
    Hits up an API to do so.
    """
    # Create folders
    CODEGEN_FOLDER.mkdir(parents=True, exist_ok=True)
    CODEMODS_FOLDER.mkdir(parents=True, exist_ok=True)
    SAMPLE_CODEMOD_PATH = CODEMODS_FOLDER / "sample_codemod.py"
    SAMPLE_CODEMOD_PATH.write_text(SAMPLE_CODEMOD)
    DOCS_FOLDER = CODEGEN_FOLDER / "docs"
    SKILLS_FOLDER = CODEGEN_FOLDER / "skills"
    DOCS_FOLDER.mkdir(parents=True, exist_ok=True)
    SKILLS_FOLDER.mkdir(parents=True, exist_ok=True)

    # Populate folders
    docs = fetch_docs(session)
    populate_api_docs(DOCS_FOLDER, docs["docs"])
    populate_examples(SKILLS_FOLDER, docs["examples"])

    click.echo("\n🚀 Codegen CLI Initialized Successfully!")
    click.echo("━" * 60)
    click.echo(get_success_message(CODEGEN_FOLDER, CODEMODS_FOLDER, DOCS_FOLDER, SKILLS_FOLDER, SAMPLE_CODEMOD_PATH))
    click.echo("━" * 60 + "\n")
