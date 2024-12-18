import shutil
from pathlib import Path

from rich.status import Status

from codegen.api.schemas import SerializedExample
from codegen.auth.session import CodegenSession
from codegen.codemod.convert import convert_to_cli
from codegen.utils.constants import ProgrammingLanguage


def populate_examples(session: CodegenSession, dest: Path, examples: list[SerializedExample], status: Status):
    """Populate the examples folder with examples for the current repository."""
    status.update("Populating example codemods...")
    # Remove existing examples
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)

    for example in examples:
        dest_file = dest / f"{example.name}.py"
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        session.config.programming_language = example.language
        session.write_config()
        formatted = format_example(example)
        dest_file.write_text(formatted)


def format_section(title: str, content: str | None) -> str:
    """Format a section with a title and optional content."""
    if not content:
        return ""
    lines = content.splitlines()
    formatted_lines = "\n    ".join(lines)
    return f"{title}:\n    {formatted_lines}"


def format_example(example: SerializedExample, language: ProgrammingLanguage) -> str:
    """Format a single example."""
    name = example.name if example.name else "Untitled"

    sections = [f"{name}-({example.language})", format_section("Description", example.description), format_section("Docstring", example.docstring)]

    return '"' * 3 + "\n".join(filter(None, sections)) + '"' * 3 + "\n\n" + convert_to_cli(example.source, language)
