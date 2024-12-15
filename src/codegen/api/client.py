from pathlib import Path
from typing import ClassVar, TypeVar

import requests
from pydantic import BaseModel

from codegen.api.endpoints import (
    CREATE_ENDPOINT,
    DOCS_ENDPOINT,
    EXPERT_ENDPOINT,
    RUN_CODEMOD_ENDPOINT,
)
from codegen.api.schemas import (
    AskExpertInput,
    AskExpertResponse,
    CreateInput,
    CreateResponse,
    DocsInput,
    DocsResponse,
    RunCodemodInput,
    RunCodemodOutput,
)
from codegen.auth.session import CodegenSession
from codegen.errors import ServerError

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class API:
    """Handles auth + validation with the codegen API."""

    _session: ClassVar[requests.Session] = requests.Session()

    @classmethod
    def _get_headers(cls) -> dict[str, str]:
        """Get headers with authentication token."""
        session = CodegenSession()
        session.assert_authenticated()
        return {
            "Authorization": f"Bearer {session.token}",
        }

    @classmethod
    def _make_request(
        cls,
        method: str,
        endpoint: str,
        input_data: InputT | None,
        output_model: type[OutputT],
    ) -> OutputT:
        """Make an API request with input validation and response handling."""
        try:
            headers = cls._get_headers()
            json_data = input_data.model_dump() if input_data else None

            response = cls._session.request(
                method,
                endpoint,
                json=json_data,
                headers=headers,
            )

            if response.status_code == 200:
                try:
                    return output_model.model_validate(response.json())
                except ValueError as e:
                    raise ServerError(f"Invalid response format: {e}")

            elif response.status_code == 500:
                raise ServerError("The server encountered an error while processing your request")

            else:
                try:
                    error_json = response.json()
                    error_msg = error_json.get("detail", error_json)
                except Exception:
                    error_msg = response.text
                raise ServerError(f"Error ({response.status_code}): {error_msg}")

        except requests.RequestException as e:
            raise ServerError(f"Network error: {e!s}")

    @classmethod
    def run(
        cls,
        repo_full_name: str,
        codemod_source: str | Path,
        web: bool = False,
    ) -> RunCodemodOutput:
        """Run a codemod transformation."""
        if isinstance(codemod_source, Path):
            codemod_source = codemod_source.read_text()

        input_data = RunCodemodInput(
            repo_full_name=repo_full_name,
            codemod_source=codemod_source,
            web=web,
        )

        return cls._make_request(
            "POST",
            RUN_CODEMOD_ENDPOINT,
            input_data,
            RunCodemodOutput,
        )

    @classmethod
    def get_docs(cls) -> dict:
        """Search documentation."""
        session = CodegenSession()
        return cls._make_request(
            "GET",
            DOCS_ENDPOINT,
            DocsInput(repo_full_name=session.repo_name, language="PYTHON"),
            DocsResponse,
        )

    @classmethod
    def ask_expert(cls, query: str) -> AskExpertResponse:
        """Ask the expert system a question."""
        return cls._make_request(
            "GET",
            EXPERT_ENDPOINT,
            AskExpertInput(query=query),
            AskExpertResponse,
        )

    @classmethod
    def create(cls, query: str) -> CreateResponse:
        """Get AI-generated starter code for a codemod."""
        return cls._make_request(
            "GET",
            CREATE_ENDPOINT,
            CreateInput(query=query),
            CreateResponse,
        )
