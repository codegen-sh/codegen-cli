from dataclasses import dataclass
from pathlib import Path
import jwt
from typing import Optional

from codegen.auth.token_manager import TokenManager, get_current_token
from codegen.utils.git.repo import get_git_repo
from codegen.utils.git.url import get_repo_full_name


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

    def __init__(self, token: Optional[str] = None):
        self._token = token or get_current_token()
        if not self._token:
            raise ValueError("No authentication token found")

        self._profile: Optional[UserProfile] = None
        self._repo_name: Optional[str] = None

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
    def repo_name(self) -> str:
        """Get the current repository name"""
        if not self._repo_name:
            git_repo = get_git_repo(Path.cwd())
            self._repo_name = get_repo_full_name(git_repo)
        return self._repo_name

    def __str__(self) -> str:
        return f"CodegenSession(user={self.profile.name}, repo={self.repo_name})"

    def is_authenticated(self) -> bool:
        """Check if the session is fully authenticated"""
        return bool(self._token and self.repo_name)
