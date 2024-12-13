from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

from codegen.api.schemas import RunCodemodOutput


def pretty_print_output(output: RunCodemodOutput):
    console = Console()
    if output.logs:
        console.print(Rule(title="Logs", align="left"))
        pretty_print_logs(output.logs)
    if output.observation:
        console.print(Rule(title="Diff", align="left"))
        pretty_print_diff(output.observation)


def pretty_print_logs(logs: str):
    console = Console()
    for line in logs.splitlines():
        console.print(line, markup=True, soft_wrap=True)


def pretty_print_diff(diff: str):
    body = Markdown(
        f"""
```diff
{diff}
```
""",
        code_theme="monokai",
    )
    rprint(body)
