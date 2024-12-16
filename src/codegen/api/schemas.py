from codegen.utils.constants import ProgrammingLanguage
from codegen.utils.schema import SafeBaseModel

###########################################################################
# RUN
###########################################################################


class RunCodemodInput(SafeBaseModel):
    codemod_id: int
    repo_full_name: str
    codemod_source: str


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
    query: str


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
    repo_full_name: str
    language: str


class DocsResponse(SafeBaseModel):
    docs: dict[str, str]
    examples: list[SerializedExample]


###########################################################################
# CREATE
###########################################################################


class CreateInput(SafeBaseModel):
    query: str | None = None
    repo_full_name: str | None = None


class CreateResponse(SafeBaseModel):
    success: bool
    response: str
    code: str
    codemod_id: int
