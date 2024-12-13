from pydantic import BaseModel


class SafeBaseModel(BaseModel):
    @classmethod
    def model_validate(cls, data: dict) -> "SafeBaseModel":
        try:
            return super().model_validate(data)
        except Exception as e:
            print(e)
            return None
