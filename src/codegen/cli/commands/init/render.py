from pathlib import Path


def get_success_message(codegen_dir: Path, codemods_dir: Path, docs_dir: Path, examples_dir: Path) -> str:
    """Get a compact success message showing created folders."""
    return (
        "📁 Folders Created:\n"
        f"   📦 Codegen:   {codegen_dir.relative_to(Path.cwd())}\n"
        f"   🔧 Codemods:  {codemods_dir.relative_to(Path.cwd())}\n"
        f"   📚 Docs:      {docs_dir.relative_to(Path.cwd())}\n"
        f"   💡 Examples:  {examples_dir.relative_to(Path.cwd())}"
    )
