from pydantic import BaseModel

from codegen.constants import ProgrammingLanguage


class SkillOutput(BaseModel):
    name: str | None
    description: str | None
    docstring: str
    source: str
    language: ProgrammingLanguage
