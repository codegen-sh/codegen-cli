from pathlib import Path

from rich.text import Text


def get_success_message(codegen_folder, codemods_folder, docs_folder, examples_folder, config_file) -> Text:
    """Create a rich-formatted success message."""
    message = Text()

    def make_relative(path: Path) -> str:
        return f"./{path.relative_to(Path.cwd())}"

    # Folders section
    message.append("\n", style="bold yellow")
    message.append("Folders Created:", style="bold blue")
    message.append("\n   📁 Codegen:   ", style="dim")
    message.append(make_relative(codegen_folder), style="cyan")
    message.append("\n   📁 Codemods:  ", style="dim")
    message.append(make_relative(codemods_folder), style="cyan")
    message.append("\n   📁 Docs:      ", style="dim")
    message.append(make_relative(docs_folder), style="cyan")
    message.append("\n   📁 Examples:  ", style="dim")
    message.append(make_relative(examples_folder), style="cyan")
    message.append("\n   🔧 Config:    ", style="dim")
    message.append(make_relative(config_file), style="cyan")

    return message
