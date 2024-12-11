import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".codegen"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """Ensure the config directory exists"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    """Load the config file or return empty dict if it doesn't exist"""
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE) as f:
        return json.load(f)
