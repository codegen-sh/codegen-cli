from codegen.models import SkillOutput


def format_section(title: str, content: str | None) -> str:
    """Format a section with a title and optional content."""
    if not content:
        return ""
    lines = content.splitlines()
    formatted_lines = "\n    ".join(lines)
    return f"{title}:\n    {formatted_lines}"


def format_skill(skill: SkillOutput) -> str:
    """Format a complete skill including name, description, docstring and source."""
    name = skill.name if skill.name else "Untitled"

    sections = [f"{name}-({skill.language})", format_section("Description", skill.description), format_section("Docstring", skill.docstring)]

    return '"' * 3 + "\n".join(filter(None, sections)) + '"' * 3 + "\n\n" + skill.source
