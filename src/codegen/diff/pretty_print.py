from rich import print as rprint
from rich.markdown import Markdown


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
