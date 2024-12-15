from codegen.utils.constants import ProgrammingLanguage
from codegen.utils.schema import SafeBaseModel


class RunCodemodInput(SafeBaseModel):
    repo_full_name: str
    codemod_source: str
    web: bool = False


class RunCodemodOutput(SafeBaseModel):
    success: bool = False
    web_link: str | None = None
    logs: str | None = None
    observation: str | None = None


class SkillOutput(SafeBaseModel):
    name: str | None
    description: str | None
    source: str
    language: ProgrammingLanguage
    docstring: str = ""
