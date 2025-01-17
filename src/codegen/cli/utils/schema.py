from typing import Self

from pydantic import BaseModel


class SafeBaseModel(BaseModel):
    @classmethod
    def model_validate(cls, data: dict) -> "Self":
        try:
            return super().model_validate(data)
        except Exception as e:
            print(e)
            return None

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)


CODEMOD_CONFIG_PATH = "config.toml"


class CodemodConfig(BaseModel):
    """Configuration for a codemod stored in the codegen-sh/codemods/<name>/config.toml file."""

    name: str
    codemod_id: int
    description: str | None = None
    created_at: str
    created_by: str