from dataclasses import dataclass
from pathlib import Path

import jwt
from pygit2.repository import Repository

from codegen.auth.config import CODEGEN_DIR, CODEMODS_DIR
from codegen.auth.token_manager import TokenManager, get_current_token
from codegen.errors import AuthError
from codegen.utils.codemods import Codemod
from codegen.utils.config import Config, State, get_config, get_state, read_model, write_config, write_state
from codegen.utils.git.repo import get_git_repo
from codegen.utils.schema import CODEMOD_CONFIG_PATH, CodemodConfig


@dataclass
class UserProfile:
    """User profile information extracted from JWT token"""

    name: str
    email: str
    username: str

    @classmethod
    def from_token(cls, token: str) -> "UserProfile":
        """Create a UserProfile from a JWT token"""
        claims = jwt.decode(token.encode("utf-8"), options={"verify_signature": False})
        user_metadata = claims.get("user_metadata", {})
        return cls(name=user_metadata.get("full_name", "N/A"), email=claims.get("email", "N/A"), username=user_metadata.get("preferred_username", "N/A"))


class CodegenSession:
    """Represents an authenticated codegen session with user and repository context"""

    config: Config
    state: State

    def __init__(self, token: str | None = None):
        self._token = token or get_current_token()
        self._profile: UserProfile | None = None
        self._repo_name: str | None = None
        self._active_codemod: Codemod | None = None
        self.config = get_config(self.codegen_dir)
        self.state = get_state(self.codegen_dir)

    @property
    def token(self) -> str:
        """Get the authentication token"""
        return self._token

    @property
    def profile(self) -> UserProfile:
        """Get the user profile information"""
        if not self._profile:
            self._profile = UserProfile.from_token(self._token)
        return self._profile

    @property
    def git_repo(self) -> Repository:
        git_repo = get_git_repo(Path.cwd())
        if not git_repo:
            raise ValueError("No git repository found")
        return git_repo

    @property
    def repo_name(self) -> str:
        """Get the current repository name"""
        return self.config.repo_full_name

    @property
    def active_codemod(self) -> Codemod | None:
        """Get the active codemod information if one exists."""
        if self._active_codemod is None:
            codemods_dir = Path.cwd() / CODEGEN_DIR / "codemods"

            codemod_dir = codemods_dir / self.state.active_codemod
            run_file = codemod_dir / "run.py"
            config_file = codemod_dir / CODEMOD_CONFIG_PATH

            if not run_file.exists():
                return None

            # Try to load config if it exists
            config = None
            if config_file.exists():
                try:
                    config = read_model(CodemodConfig, config_file)
                except Exception:
                    pass  # Config is optional

            self._active_codemod = Codemod(name=self.state.active_codemod, path=run_file, config=config)

        return self._active_codemod

    @property
    def codegen_dir(self) -> Path:
        """Get the path to the  codegen-sh directory"""
        return Path.cwd() / CODEGEN_DIR

    @property
    def codemods_dir(self) -> Path:
        """Get the path to the codemods directory"""
        return Path.cwd() / CODEMODS_DIR

    def __str__(self) -> str:
        return f"CodegenSession(user={self.profile.name}, repo={self.repo_name})"

    def is_authenticated(self) -> bool:
        """Check if the session is fully authenticated, including token expiration"""
        return bool(self._token and TokenManager().validate_expiration(self._token))

    def assert_authenticated(self) -> None:
        """Raise an AuthError if the session is not fully authenticated"""
        if not self._token:
            raise AuthError("No authentication token found")
        if not TokenManager().validate_expiration(self._token):
            raise AuthError("Authentication token has expired")

    def write_config(self) -> None:
        """Write the config to the codegen-sh/config.toml file"""
        write_config(self.config, self.codegen_dir)

    def write_state(self) -> None:
        """Write the state to the codegen-sh/state.toml file"""
        write_state(self.state, self.codegen_dir)
