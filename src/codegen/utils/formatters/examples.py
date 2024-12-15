from codegen.api.schemas import SerializedExample


def format_section(title: str, content: str | None) -> str:
    """Format a section with a title and optional content."""
    if not content:
        return ""
    lines = content.splitlines()
    formatted_lines = "\n    ".join(lines)
    return f"{title}:\n    {formatted_lines}"


def format_example(example: SerializedExample) -> str:
    """Format a single example."""
    name = example.name if example.name else "Untitled"

    sections = [f"{name}-({example.language})", format_section("Description", example.description), format_section("Docstring", example.docstring)]

    return '"' * 3 + "\n".join(filter(None, sections)) + '"' * 3 + "\n\n" + example.source
