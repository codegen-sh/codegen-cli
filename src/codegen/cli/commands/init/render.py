from pathlib import Path


def get_success_message(codegen_dir: Path, docs_dir: Path, examples_dir: Path) -> str:
    """Get the success message to display after initialization."""
    return f"""📁 Folders Created:
   📦 Location:  ./{codegen_dir.relative_to(Path.cwd())}
   📚 Docs:      ./{docs_dir.relative_to(Path.cwd())}
   🔧 Examples:  ./{examples_dir.relative_to(Path.cwd())}"""
