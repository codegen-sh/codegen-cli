# This utility contains functions for utilizing, transforming and validating JSON schemas generated by Pydantic models.

import json

from pydantic import BaseModel


def get_schema(model: BaseModel) -> dict:
    return model.model_json_schema()

from pathlib import Path
from tempfile import TemporaryDirectory

from datamodel_code_generator import DataModelType, InputFileType, generate


def validate_json(schema: dict, json_data: str) -> bool:
    json_schema = json.dumps(schema)
    exec_scope = {}
    model_name = schema['title']
    with TemporaryDirectory() as temporary_directory_name:
        temporary_directory = Path(temporary_directory_name)
        output = Path(temporary_directory / 'model.py')
        generate(
            json_schema,
            input_file_type=InputFileType.JsonSchema,
            input_filename="temp.json",
            output=output,
            # set up the output model types
            output_model_type=DataModelType.PydanticV2BaseModel,
        )

        exec(output.read_text(), exec_scope, exec_scope)
    print(f"exec_scope: {exec_scope}")
    model = exec_scope.get(model_name)
    try:
        model.model_validate_json(json_data)
        return True
    except Exception as e:
        return False
