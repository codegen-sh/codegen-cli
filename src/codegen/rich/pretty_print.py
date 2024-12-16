from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from codegen.api.schemas import RunCodemodOutput


def pretty_print_output(output: RunCodemodOutput):
    """Pretty print the codemod run output with panels."""
    console = Console()

    if output.web_link:
        console.print("\n• [blue underline]" + output.web_link + "[/blue underline]\n")

    if output.logs:
        console.print(
            Panel(
                output.logs,
                title="[bold blue]Logs",
                border_style="blue",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        console.print()  # Add spacing

    if output.error:
        console.print(
            Panel(
                output.error,
                title="[bold red]Error",
                border_style="red",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        console.print()  # Add spacing

    if output.observation:
        console.print(
            Panel(
                Markdown(
                    f"""```diff\n{output.observation}\n```""",
                    code_theme="monokai",
                ),
                title="[bold green]Diff",
                border_style="green",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        console.print()  # Add spacing


def pretty_print_logs(logs: str):
    """Pretty print logs in a panel."""
    console = Console()
    console.print(
        Panel(
            logs,
            title="[bold blue]Logs",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def pretty_print_diff(diff: str):
    """Pretty print diff in a panel."""
    console = Console()
    console.print(
        Panel(
            Markdown(
                f"""```diff\n{diff}\n```""",
                code_theme="monokai",
            ),
            title="[bold green]Diff",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
