from enum import Enum
from typing import TypeVar

from pydantic import BaseModel, Field

from codegen.cli.utils.constants import ProgrammingLanguage
from codegen.cli.utils.schema import SafeBaseModel

T = TypeVar("T")


###########################################################################
# RUN
###########################################################################


class CodemodRunType(str, Enum):
    """Type of codemod run."""

    DIFF = "diff"
    PR = "pr"


class RunCodemodInput(SafeBaseModel):
    class BaseRunCodemodInput(SafeBaseModel):
        repo_full_name: str
        codemod_id: int | None = None
        codemod_name: str | None = None
        codemod_source: str | None = None
        codemod_run_type: CodemodRunType = CodemodRunType.DIFF
        template_context: dict[str, str] = Field(default_factory=dict)

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
    language: ProgrammingLanguage


###########################################################################
# CREATE
###########################################################################


class CreateInput(SafeBaseModel):
    class BaseCreateInput(SafeBaseModel):
        name: str
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


###########################################################################
# DEPLOY
###########################################################################


class DeployInput(BaseModel):
    """Input for deploying a codemod."""

    class BaseDeployInput(BaseModel):
        codemod_name: str = Field(..., description="Name of the codemod to deploy")
        codemod_source: str = Field(..., description="Source code of the codemod")
        repo_full_name: str = Field(..., description="Full name of the repository")
        lint_mode: bool = Field(default=False, description="Whether this is a PR check/lint mode function")
        lint_user_whitelist: list[str] = Field(default_factory=list, description="List of GitHub usernames to notify")
        message: str | None = Field(default=None, description="Optional message describing the codemod being deployed.")
        arguments_schema: dict | None = Field(default=None, description="Schema of the arguments parameter")

    input: BaseDeployInput = Field(..., description="Input data for deployment")


class DeployResponse(BaseModel):
    """Response from deploying a codemod."""

    success: bool = Field(..., description="Whether the deployment was successful")
    new: bool = Field(..., description="Whether the codemod is newly created")
    codemod_id: int = Field(..., description="ID of the deployed codemod")
    version_id: int = Field(..., description="Version ID of the deployed codemod")
    url: str = Field(..., description="URL of the deployed codemod")


###########################################################################
# LOOKUP
###########################################################################


class LookupInput(BaseModel):
    """Input for looking up a codemod."""

    class BaseLookupInput(BaseModel):
        codemod_name: str = Field(..., description="Name of the codemod to look up")
        repo_full_name: str = Field(..., description="Full name of the repository")

    input: BaseLookupInput = Field(..., description="Input data for lookup")


class LookupOutput(BaseModel):
    """Response from looking up a codemod."""

    codemod_id: int = Field(..., description="ID of the codemod")
    version_id: int = Field(..., description="Version ID of the codemod")


###########################################################################
# PR LOOKUP
###########################################################################


class PRSchema(BaseModel):
    url: str
    title: str
    body: str
    github_pr_number: int
    codegen_pr_id: int


class PRLookupInput(BaseModel):
    class BasePRLookupInput(BaseModel):
        repo_full_name: str
        github_pr_number: int

    input: BasePRLookupInput


class PRLookupResponse(BaseModel):
    pr: PRSchema


###########################################################################
# TEST WEBHOOK
###########################################################################


class RunOnPRInput(BaseModel):
    """Input for testing a webhook against a PR."""

    class BaseRunOnPRInput(BaseModel):
        codemod_name: str = Field(..., description="Name of the codemod to test")
        repo_full_name: str = Field(..., description="Full name of the repository")
        github_pr_number: int = Field(..., description="GitHub PR number to test against")
        language: str | None = Field(..., description="Language of the codemod")

    input: BaseRunOnPRInput = Field(..., description="Input data for webhook test")


class RunOnPRResponse(BaseModel):
    """Response from testing a webhook."""

    codemod_id: int = Field(..., description="ID of the codemod")
    codemod_run_id: int = Field(..., description="ID of the codemod run")
    web_url: str = Field(..., description="URL to view the test results")
