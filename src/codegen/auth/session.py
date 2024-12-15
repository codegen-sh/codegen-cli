from dataclasses import dataclass
from pathlib import Path

import jwt
from pygit2.repository import Repository

from codegen.auth.token_manager import TokenManager, get_current_token
from codegen.errors import AuthError
from codegen.utils.codemods import Codemod
from codegen.utils.git.repo import get_git_repo
from codegen.utils.git.url import get_repo_full_name
from codegen.utils.schema import CodemodConfig


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

    def __init__(self, token: str | None = None):
        self._token = token or get_current_token()
        if not self._token:
            raise ValueError("No authentication token found")

        self._profile: UserProfile | None = None
        self._repo_name: str | None = None
        self._active_codemod: Codemod | None = None

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
        if not self._repo_name:
            git_repo = self.git_repo
            self._repo_name = get_repo_full_name(git_repo)
        return self._repo_name

    @property
    def active_codemod(self) -> Codemod | None:
        """Get the active codemod information if one exists."""
        if self._active_codemod is None:
            codemods_dir = Path.cwd() / ".codegen" / "codemods"
            active_codemod_file = codemods_dir / "active_codemod.txt"

            if not active_codemod_file.exists():
                return None

            active_codemod = active_codemod_file.read_text().strip()
            codemod_dir = codemods_dir / active_codemod
            run_file = codemod_dir / "run.py"
            config_file = codemod_dir / "config.json"

            if not run_file.exists():
                return None

            # Try to load config if it exists
            config = None
            if config_file.exists():
                try:
                    config = CodemodConfig.model_validate_json(config_file.read_text())
                except Exception:
                    pass  # Config is optional

            self._active_codemod = Codemod(name=active_codemod, path=run_file, config=config)

        return self._active_codemod

    def __str__(self) -> str:
        return f"CodegenSession(user={self.profile.name}, repo={self.repo_name})"

    def is_authenticated(self) -> bool:
        """Check if the session is fully authenticated, including token expiration"""
        return bool(self._token and self.repo_name and TokenManager().validate_expiration(self._token))

    def assert_authenticated(self) -> None:
        """Raise an AuthError if the session is not fully authenticated"""
        if not self._token:
            raise AuthError("No authentication token found")
        if not self.repo_name:
            raise AuthError("No repository found")
        if not TokenManager().validate_expiration(self._token):
            raise AuthError("Authentication token has expired")
