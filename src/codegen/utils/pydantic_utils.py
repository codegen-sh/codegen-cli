from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def safe_parse_json(json_obj: dict, model: type[T]) -> T | None:
    try:
        return model.model_validate(json_obj)
    except Exception as e:
        print(e)
        return None
