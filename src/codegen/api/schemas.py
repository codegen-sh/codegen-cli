from typing import TypeVar

from codegen.utils.constants import ProgrammingLanguage
from codegen.utils.schema import SafeBaseModel

T = TypeVar("T")


###########################################################################
# RUN
###########################################################################


class RunCodemodInput(SafeBaseModel):
    class BaseRunCodemodInput(SafeBaseModel):
        codemod_id: int
        repo_full_name: str
        codemod_source: str

    input: BaseRunCodemodInput


class RunCodemodOutput(SafeBaseModel):
    success: bool = False
    web_link: str | None = None
    logs: str | None = None
    observation: str | None = None
    error: str | None = None


###########################################################################
# EXPERT
###########################################################################


class AskExpertInput(SafeBaseModel):
    class BaseAskExpertInput(SafeBaseModel):
        query: str

    input: BaseAskExpertInput


class AskExpertResponse(SafeBaseModel):
    response: str
    success: bool


###########################################################################
# DOCS
###########################################################################


class SerializedExample(SafeBaseModel):
    name: str | None
    description: str | None
    source: str
    language: ProgrammingLanguage
    docstring: str = ""


class DocsInput(SafeBaseModel):
    class BaseDocsInput(SafeBaseModel):
        repo_full_name: str

    docs_input: BaseDocsInput


class DocsResponse(SafeBaseModel):
    docs: dict[str, str]
    examples: list[SerializedExample]


###########################################################################
# CREATE
###########################################################################


class CreateInput(SafeBaseModel):
    class BaseCreateInput(SafeBaseModel):
        query: str | None = None
        repo_full_name: str | None = None

    input: BaseCreateInput


class CreateResponse(SafeBaseModel):
    success: bool
    response: str
    code: str
    codemod_id: int
    context: str | None = None


###########################################################################
# IDENTIFY
###########################################################################


class IdentifyResponse(SafeBaseModel):
    class AuthContext(SafeBaseModel):
        token_id: int
        expires_at: str
        status: str
        user_id: int

    class User(SafeBaseModel):
        github_user_id: str
        avatar_url: str
        auth_user_id: str
        created_at: str
        email: str
        is_contractor: str | None
        github_username: str
        full_name: str | None
        id: int
        last_updated_at: str | None

    auth_context: AuthContext
    user: User
