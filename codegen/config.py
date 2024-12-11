import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".codegen"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """Ensure the config directory exists"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save_token(token: str):
    """Save the auth token to config file"""
    ensure_config_dir()
    config = load_config()
    config["auth_token"] = token

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


def load_config() -> dict:
    """Load the config file or return empty dict if it doesn't exist"""
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE) as f:
        return json.load(f)


def get_token() -> str | None:
    """Get the auth token if it exists"""
    config = load_config()
    return config.get("auth_token")
