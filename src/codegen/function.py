from dataclasses import dataclass
from typing import Optional

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.session import CodegenSession


@dataclass
class PullRequest:
    """A pull request created by a codemod."""

    url: str
    number: int
    title: str


@dataclass
class Function:
    """A deployed codegen function that can be run."""

    name: str
    codemod_id: int
    version_id: int
    _api_client: Optional[RestAPI] = None

    @classmethod
    def lookup(cls, name: str) -> "Function":
        """Look up a deployed function by name."""
        session = CodegenSession()
        api_client = RestAPI(session.token)
        response = api_client.lookup(name)

        return cls(name=name, codemod_id=response.codemod_id, version_id=response.version_id, _api_client=api_client)

    def run(self, pr: bool = False, **kwargs) -> Optional[PullRequest]:
        """Run the function with the given arguments."""
        if self._api_client is None:
            session = CodegenSession()
            self._api_client = RestAPI(session.token)

        # TODO: Implement the run functionality
        # This will need to be implemented once we have the run endpoint ready
        raise NotImplementedError("Run functionality coming soon!")
