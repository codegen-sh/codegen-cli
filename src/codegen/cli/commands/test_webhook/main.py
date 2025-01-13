import rich
import rich_click as click

from codegen.cli.api.client import RestAPI
from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.codemod_manager import CodemodManager


def test_webhook(session: CodegenSession, codemod_name: str, pr_number: int) -> None:
    """Test a webhook against a specific PR."""
    # Find the codemod
    codemod = CodemodManager.get(codemod_name)
    if not codemod:
        raise click.ClickException(f"No function found with name '{codemod_name}'")

    with create_spinner(f"Testing webhook '{codemod_name}' on PR #{pr_number}...") as status:
        try:
            response = RestAPI(session.token).test_webhook(
                codemod_name=codemod_name,
                repo_full_name=session.repo_name,
                github_pr_number=pr_number,
            )
            status.stop()
            rich.print(f"✅ Webhook test completed for PR #{pr_number}")
            rich.print(f"   [dim]View results:[/dim] [blue underline]{response.web_url}[/blue underline]")
        except Exception as e:
            status.stop()
            raise click.ClickException(f"Failed to test webhook: {e!s}")


@click.command(name="test-webhook")
@requires_auth
@click.argument("codemod_name", type=str)
@click.argument("pr_number", type=int)
def test_webhook_command(session: CodegenSession, codemod_name: str, pr_number: int):
    """Test a webhook against a specific PR.

    CODEMOD_NAME is the name of the codemod to test
    PR_NUMBER is the GitHub PR number to test against
    """
    test_webhook(session, codemod_name, pr_number)
