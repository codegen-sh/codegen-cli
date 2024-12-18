from rich.text import Text


def get_success_message(codegen_folder, codemods_folder, docs_folder, examples_folder) -> Text:
    """Create a rich-formatted success message."""
    message = Text()

    # Folders section
    message.append("\n📁 ", style="bold yellow")
    message.append("Folders Created:", style="bold blue")
    message.append("\n   • Codegen:  ", style="dim")
    message.append(str(codegen_folder), style="cyan")
    message.append("\n   • Codemods: ", style="dim")
    message.append(str(codemods_folder), style="cyan")
    message.append("\n   • Docs:     ", style="dim")
    message.append(str(docs_folder), style="cyan")
    message.append("\n   • Examples: ", style="dim")
    message.append(str(examples_folder), style="cyan")

    return message
