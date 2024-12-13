from pydantic import BaseModel

from codegen.utils.constants import ProgrammingLanguage


class RunCodemodOutput(BaseModel):
    success: bool = False
    web_link: str | None = None
    logs: str | None = None
    observation: str | None = None


class SkillOutput(BaseModel):
    name: str | None
    description: str | None
    docstring: str
    source: str
    language: ProgrammingLanguage
