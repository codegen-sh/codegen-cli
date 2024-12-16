import json
import os
from datetime import UTC, datetime
from pathlib import Path

import jwt
import jwt.exceptions

from codegen.auth.config import CONFIG_DIR, AUTH_FILE


class TokenManager:
    # Simple token manager to store and retrieve tokens.
    # This manager checks if the token is expired before retrieval.
    # TODO: add support for refreshing token and re authorization via supabase oauth
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.token_file = AUTH_FILE
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        if not os.path.exists(self.config_dir):
            Path(self.config_dir).mkdir(parents=True, exist_ok=True)

    def save_token(self, token: str) -> None:
        """Save JWT token to disk."""
        try:
            # Verify token is valid JWT before saving
            jwt.decode(token, options={"verify_signature": False})

            with open(self.token_file, "w") as f:
                json.dump({"token": token}, f)

            # Secure the file permissions (read/write for owner only)
            os.chmod(self.token_file, 0o600)
        except jwt.InvalidTokenError as e:
            print(e)
            raise ValueError("Invalid JWT token provided") from e
        except Exception as e:
            print(f"Error saving token: {e!s}")
            raise

    def get_token(self) -> str | None:
        """Retrieve token from disk if it exists and is valid."""
        try:
            if not os.access(self.config_dir, os.R_OK):
                return None

            if not os.path.exists(self.token_file):
                return None

            with open(self.token_file) as f:
                data = json.load(f)
                token = data.get("token")
                if not token:
                    return None

                if not self.validate_expiration(token):
                    print("Expired token - reauthenticate with `codegen login`")
                    self.clear_token()
                    return None

                return token

        except (json.JSONDecodeError, jwt.InvalidTokenError, KeyError, OSError) as e:
            print(e)
            return None

    def validate_expiration(self, token: str) -> bool:
        """Validate the expiration of a token."""
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        return exp > datetime.now(UTC)

    def clear_token(self) -> None:
        """Remove stored token."""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)


def get_current_token() -> str | None:
    """Get the current authentication token if one exists.

    This is a helper function that creates a TokenManager instance and retrieves
    the stored token. The token is validated before being returned.

    Returns:
        Optional[str]: The current valid JWT token if one exists and hasn't expired.
                      Returns None if no token exists, the token is expired, or invalid.

    """
    token_manager = TokenManager()
    return token_manager.get_token()
