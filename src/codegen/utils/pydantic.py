from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def safe_parse_json(json_data: str, model: type[T]) -> T | None:
    try:
        return model.model_validate_json(json_data)
    except ValidationError as e:
        return None
    except Exception as e:
        print(e)
        return None
