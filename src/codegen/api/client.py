import json
from typing import ClassVar, TypeVar

import requests
from pydantic import BaseModel
from rich import print as rprint

from codegen.api.endpoints import (
    CREATE_ENDPOINT,
    DOCS_ENDPOINT,
    EXPERT_ENDPOINT,
    IDENTIFY_ENDPOINT,
    RUN_ENDPOINT,
)
from codegen.api.schemas import (
    AskExpertInput,
    AskExpertResponse,
    CreateInput,
    CreateResponse,
    DocsInput,
    DocsResponse,
    IdentifyResponse,
    RunCodemodInput,
    RunCodemodOutput,
)
from codegen.auth.session import CodegenSession
from codegen.codemod.convert import convert_to_ui
from codegen.env.global_env import global_env
from codegen.errors import ServerError
from codegen.utils.codemods import Codemod

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class RestAPI:
    """Handles auth + validation with the codegen API."""

    _session: ClassVar[requests.Session] = requests.Session()

    auth_token: str | None = None

    def __init__(self, auth_token: str):
        self.auth_token = auth_token

    def _get_headers(self) -> dict[str, str]:
        """Get headers with authentication token."""
        return {
            "Authorization": f"Bearer {self.auth_token}",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        input_data: InputT | None,
        output_model: type[OutputT],
    ) -> OutputT:
        """Make an API request with input validation and response handling."""
        if global_env.DEBUG:
            rprint(f"[purple]{method}[/purple] {endpoint}")
            if input_data:
                rprint(f"{json.dumps(input_data.model_dump(), indent=4)}")

        try:
            headers = self._get_headers()

            json_data = input_data.model_dump() if input_data else None

            response = self._session.request(
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

    def run(
        self,
        codemod: Codemod,
    ) -> RunCodemodOutput:
        """Run a codemod transformation."""
        session = CodegenSession()

        input_data = RunCodemodInput(
            input=RunCodemodInput.BaseRunCodemodInput(
                codemod_id=codemod.config.codemod_id,
                codemod_source=convert_to_ui(codemod.get_current_source()),
                repo_full_name=session.repo_name,
            )
        )
        return self._make_request(
            "POST",
            RUN_ENDPOINT,
            input_data,
            RunCodemodOutput,
        )

    def get_docs(self) -> dict:
        """Search documentation."""
        session = CodegenSession()
        return self._make_request(
            "GET",
            DOCS_ENDPOINT,
            DocsInput(docs_input=DocsInput.BaseDocsInput(repo_full_name=session.repo_name)),
            DocsResponse,
        )

    def ask_expert(self, query: str) -> AskExpertResponse:
        """Ask the expert system a question."""
        return self._make_request(
            "GET",
            EXPERT_ENDPOINT,
            AskExpertInput(input=AskExpertInput.BaseAskExpertInput(query=query)),
            AskExpertResponse,
        )

    def create(self, query: str) -> CreateResponse:
        """Get AI-generated starter code for a codemod."""
        session = CodegenSession()
        return self._make_request(
            "GET",
            CREATE_ENDPOINT,
            CreateInput(input=CreateInput.BaseCreateInput(query=query, repo_full_name=session.repo_name)),
            CreateResponse,
        )

    def identify(self) -> IdentifyResponse | None:
        """Identify the user's codemod."""
        try:
            return self._make_request(
                "POST",
                IDENTIFY_ENDPOINT,
                None,
                IdentifyResponse,
            )
        except ServerError as e:
            print(f"Error identifying user: {e}")
            return None
