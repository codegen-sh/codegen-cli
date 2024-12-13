from requests import Response

from codegen.api.schemas import RunCodemodOutput
from codegen.diff.pretty_print import pretty_print_diff
from codegen.utils.pydantic_utils import safe_parse_json


def run_200_handler(payload: dict, response: Response):
    run_output = safe_parse_json(response.json(), RunCodemodOutput)
    if not run_output:
        print(f"422 UnprocessableEntity: {response.json()}")
        return
    if not run_output.success:
        print(f"500 InternalServerError: {run_output.observation}")
        return
    if payload.get("web"):
        # TODO: also open in the browser
        print(run_output.web_link)
        return

    pretty_print_diff(run_output.logs)
