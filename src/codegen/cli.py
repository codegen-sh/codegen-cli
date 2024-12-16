import rich_click as click

from codegen.commands.create import create_command
from codegen.commands.docs_search import docs_search_command
from codegen.commands.expert import expert_command
from codegen.commands.init import init_command
from codegen.commands.login import login_command
from codegen.commands.logout import logout_command
from codegen.commands.profile import profile_command
from codegen.commands.run import run_command
from codegen.commands.set_active import set_active_command
from codegen.errors import handle_errors


@click.group()
def main():
    """Codegen CLI - Transform your code with AI."""


# Wrap commands with error handler
main.add_command(handle_errors(init_command))
main.add_command(handle_errors(logout_command))
main.add_command(handle_errors(login_command))
main.add_command(handle_errors(run_command))
main.add_command(handle_errors(docs_search_command))
main.add_command(handle_errors(profile_command))
main.add_command(handle_errors(create_command))
main.add_command(handle_errors(expert_command))
main.add_command(set_active_command)

if __name__ == "__main__":
    main()
