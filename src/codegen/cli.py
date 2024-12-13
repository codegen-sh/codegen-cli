import click

from codegen.commands.docs_search import docs_search_command
from codegen.commands.init import init_command
from codegen.commands.login import login_command
from codegen.commands.logout import logout_command
from codegen.commands.run import run_command
from codegen.env.global_env import global_env


@click.group()
def main():
    """Codegen CLI - Transform your code with AI."""
    print(f"ENV: {global_env.ENV}")


# projects
main.add_command(init_command)

# auth
main.add_command(logout_command)
main.add_command(login_command)

# run
main.add_command(run_command)

# docs
main.add_command(docs_search_command)

if __name__ == "__main__":
    main()
