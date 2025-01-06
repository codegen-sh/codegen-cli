import webbrowser

import rich
import rich_click as click
from rich.panel import Panel
from rich.status import Status

from codegen.analytics.decorators import track_command
from codegen.api.client import RestAPI
from codegen.auth.decorators import requires_auth
from codegen.auth.session import CodegenSession
from codegen.errors import ServerError
from codegen.git.patch import apply_patch
from codegen.utils.codemod_manager import CodemodManager
from codegen.workspace.decorators import requires_init


@click.command(name="run")
@track_command()
@requires_auth
@requires_init
@click.argument("codemod_name", required=True)
@click.option("--web", is_flag=True, help="Automatically open the diff in the web app")
@click.option("--apply-local", is_flag=True, help="Applies the generated diff to the repository")
def run_command(session: CodegenSession, codemod_name: str, web: bool = False, apply_local: bool = False):
    """Run code transformation on the provided Python code."""
    active_codemod = CodemodManager.get(codemod_name)
    if not active_codemod:
        raise click.ClickException(f"Codemod '{codemod_name}' not found. Run 'codegen list' to see available codemods.")

    status = Status(f"Running {active_codemod.name}...", spinner="dots", spinner_style="purple")
    status.start()

    try:
        run_output = RestAPI(session.token).run(
            codemod=active_codemod,
        )

        status.stop()
        rich.print(f"[green]✓[/green] Ran {active_codemod.name} successfully")
        if run_output.web_link:
            rich.print(f"[blue]→[/blue] Web viewer (for humans): {run_output.web_link}")

        if run_output.logs:
            rich.print("")
            panel = Panel(run_output.logs, title="[bold]Logs[/bold]", border_style="blue", padding=(1, 2), expand=False)
            rich.print(panel)

        if run_output.error:
            rich.print("")
            panel = Panel(run_output.error, title="[bold]Error[/bold]", border_style="red", padding=(1, 2), expand=False)
            rich.print(panel)

        if run_output.observation:
            rich.print("")  # Add some spacing

            # Split and limit diff to 100 lines
            diff_lines = run_output.observation.splitlines()
            truncated = len(diff_lines) > 100
            limited_diff = "\n".join(diff_lines[:100])

            if truncated:
                if apply_local:
                    limited_diff += "\n\n...\n\n[yellow]diff truncated to 100 lines, view the full change set in your local file system[/yellow]"
                else:
                    limited_diff += "\n\n...\n\n[yellow]diff truncated to 100 lines, view the full change set on your local file system after using run with `--apply-local`[/yellow]"

            panel = Panel(limited_diff, title="[bold]Diff Preview[/bold]", border_style="blue", padding=(1, 2), expand=False)
            rich.print(panel)

            if not apply_local and not truncated:
                rich.print("")
                rich.print(f"[yellow]→ Run 'codegen run {active_codemod.name} --apply-local' to apply these changes[/yellow]")
        else:
            rich.print("")
            rich.print("[yellow]ℹ No changes were produced by this codemod[/yellow]")

        if web and run_output.web_link:
            webbrowser.open_new(run_output.web_link)

        if apply_local and run_output.observation:
            try:
                apply_patch(session.git_repo, f"\n{run_output.observation}\n")
                rich.print("")
                rich.print("[green]✓ Changes have been applied to your local filesystem[/green]")
                rich.print("[yellow]→ Don't forget to commit your changes:[/yellow]")
                rich.print("  [blue]git add .[/blue]")
                rich.print("  [blue]git commit -m 'Applied codemod changes'[/blue]")
            except Exception as e:
                rich.print("")
                rich.print("[red]✗ Failed to apply changes locally[/red]")
                rich.print("\n[yellow]This usually happens when you have uncommitted changes.[/yellow]")
                rich.print("\nOption 1 - Save your changes:")
                rich.print("  1. [blue]git status[/blue]        (check your working directory)")
                rich.print("  2. [blue]git add .[/blue]         (stage your changes)")
                rich.print("  3. [blue]git commit -m 'msg'[/blue]  (commit your changes)")
                rich.print("  4. Run this command again")
                rich.print("\nOption 2 - Discard your changes:")
                rich.print("  1. [red]git reset --hard HEAD[/red]     (⚠️ discards all uncommitted changes)")
                rich.print("  2. [red]git clean -fd[/red]            (⚠️ removes all untracked files)")
                rich.print("  3. Run this command again\n")
                raise click.ClickException("Failed to apply patch to local filesystem")

    except ServerError as e:
        status.stop()
        raise click.ClickException(str(e))
    finally:
        status.stop()
