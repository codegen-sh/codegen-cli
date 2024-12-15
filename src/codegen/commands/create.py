from datetime import datetime
from pathlib import Path

import click

from codegen.analytics.decorators import track_command
from codegen.auth.decorator import requires_auth
from codegen.auth.decorator import requires_init
from codegen.auth.session import CodegenSession


def get_codemod_template(description: str, author: str, date: str) -> str:
    return f'''"""
{description}

Created by: {author}
Date: {date}
"""
from typing import Any

def run(codebase: Any) -> None:
    """
    Your codemod logic goes here.

    Args:
        codebase: The codebase object containing files and symbols
    """
    # Example: Print all Python files
    for file in codebase.files:
        if file.path.endswith(".py"):
            print(f"Found Python file: {{file.path}}")

    # Example: Modify files
    # file = codebase.get_file("example.py")
    # file.edit("New content")

    # Example: Work with functions
    # for func in codebase.functions:
    #     if func.name.startswith("test_"):
    #         func.rename(func.name.replace("test_", ""))
'''


@click.command(name="create")
@track_command()
@requires_auth
@requires_init
@click.argument("name", type=str)
@click.option("--description", "-d", default="A codemod to transform your code", help="Description of what this codemod does")
def create_command(session: CodegenSession, name: str, description: str):
    """Create a new codemod in the .codegen/codemods directory."""
    # Ensure valid codemod name (convert to snake_case if needed)
    codemod_name = name.lower().replace(" ", "_").replace("-", "_")

    # Setup paths
    codemods_dir = Path.cwd() / ".codegen" / "codemods"
    codemod_dir = codemods_dir / codemod_name
    run_file = codemod_dir / "run.py"
    config_file = codemod_dir / "config.json"

    # Create directories
    codemods_dir.mkdir(parents=True, exist_ok=True)

    if codemod_dir.exists():
        raise click.ClickException(f"Codemod '{codemod_name}' already exists at {codemod_dir}")

    # Create codemod directory and files
    codemod_dir.mkdir()

    # Create run.py with template
    with run_file.open("w") as f:
        value = get_codemod_template(description=description, author=session.profile.name, date=datetime.now().strftime("%Y-%m-%d"))
        f.write(value)

    # Set this as the active codemod
    with (codemods_dir / "active_codemod.txt").open("w") as f:
        f.write(codemod_name)

    click.echo(f"\n✨ Created new codemod: {codemod_name}")
    click.echo("─" * 40)
    click.echo(f"Location: {codemod_dir}")
    click.echo(f"Main file: {run_file}")
    click.echo("\n💡 Next steps:")
    click.echo("1. Edit run.py to implement your codemod")
    click.echo("2. Run it with: codegen run")
    click.echo("─" * 40 + "\n")
