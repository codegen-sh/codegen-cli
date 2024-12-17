from pathlib import Path

# Base directories
CONFIG_DIR = Path("~/.config/codegen-sh").expanduser()
CODEGEN_DIR = Path("codegen-sh")

# Subdirectories
CODEMODS_DIR = CODEGEN_DIR / "codemods"
DOCS_DIR = CODEGEN_DIR / "docs"
EXAMPLES_DIR = CODEGEN_DIR / "examples"

# Files
AUTH_FILE = CONFIG_DIR / "auth.json"
ANALYTICS_FILE = CONFIG_DIR / "analytics.json"
ACTIVE_CODEMOD_FILE = CODEMODS_DIR / "active_codemod.txt"
