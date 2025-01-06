from dataclasses import dataclass
from pathlib import Path

from pygit2.repository import Repository

from codegen.auth.config import CODEGEN_DIR, CODEMODS_DIR
from codegen.auth.token_manager import get_current_token
from codegen.errors import AuthError, InvalidTokenError, NoTokenError
from codegen.git.repo import get_git_repo
from codegen.utils.config import Config, get_config, write_config


@dataclass
class Identity:
    token: str
    expires_at: str
    status: str
    user: "User"


@dataclass
class User:
    full_name: str
    email: str
    github_username: str


@dataclass
class UserProfile:
    """User profile populated from /identity endpoint"""

    name: str
    email: str
    username: str


class CodegenSession:
    """Represents an authenticated codegen session with user and repository context"""

    config: Config

    def __init__(self, token: str | None = None):
        self._token = token or get_current_token()
        self._identity: Identity | None = None
        self._profile: UserProfile | None = None
        self._repo_name: str | None = None
        self.config = get_config(self.codegen_dir)

    @property
    def identity(self) -> Identity:
        """Get the identity of the user, if a token has been provided"""
        if not self._identity and self._token:
            from codegen.api.client import RestAPI

            try:
                identity = RestAPI(self._token).identify()
                if identity:
                    self._identity = Identity(
                        token=self._token,
                        expires_at=identity.auth_context.expires_at,
                        status=identity.auth_context.status,
                        user=User(
                            full_name=identity.user.full_name,
                            email=identity.user.email,
                            github_username=identity.user.github_username,
                        ),
                    )
                    return self._identity
                else:
                    raise InvalidTokenError("Invalid authentication token")
            except InvalidTokenError:
                raise
            except Exception as e:
                raise AuthError(f"Failed to identify user: {e}")
        elif not self._token:
            raise NoTokenError("No authentication token found")
        elif self._identity:
            return self._identity

    @property
    def token(self) -> str:
        """Get the authentication token"""
        return self._token

    @property
    def profile(self) -> UserProfile:
        """Get the user profile information"""
        if not self._profile:
            identity = self.identity
            self._profile = UserProfile(
                name=identity.user.full_name,
                email=identity.user.email,
                username=identity.user.github_username,
            )
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
        return bool(self.identity and self.identity.status == "active")

    def assert_authenticated(self) -> None:
        """Raise an AuthError if the session is not fully authenticated"""
        if not self.identity:
            raise AuthError("No identity found for session")
        if self.identity.status != "active":
            raise AuthError("Current session is not active. API Token may be invalid or may have expired.")

    def write_config(self) -> None:
        """Write the config to the codegen-sh/config.toml file"""
        write_config(self.config, self.codegen_dir)
