from requests import Response
from rich.json import JSON

from codegen.api.schemas import RunCodemodOutput
from codegen.rich.pretty_print import pretty_print_output


def run_200_handler(payload: dict, response: Response):
    run_output = RunCodemodOutput.model_validate(response.json())
    if not run_output:
        print(f"422 UnprocessableEntity: {JSON(response.text)}")
        return
    if not run_output.success:
        print(f"500 InternalServerError: {run_output.observation}")
        return
    if payload.get("web"):
        # TODO: also open in the browser
        print(run_output.web_link)
        return

    pretty_print_output(run_output)
