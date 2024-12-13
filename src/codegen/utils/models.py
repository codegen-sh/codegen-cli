from pydantic import BaseModel

from codegen.utils.constants import ProgrammingLanguage


class SkillOutput(BaseModel):
    name: str | None
    description: str | None
    docstring: str
    source: str
    language: ProgrammingLanguage
