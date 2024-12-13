from codegen.utils.constants import ProgrammingLanguage
from codegen.utils.schema import SafeBaseModel


class RunCodemodOutput(SafeBaseModel):
    success: bool = False
    web_link: str | None = None
    logs: str | None = None
    observation: str | None = None


class SkillOutput(SafeBaseModel):
    name: str | None
    description: str | None
    docstring: str
    source: str
    language: ProgrammingLanguage
