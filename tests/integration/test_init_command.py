import subprocess
from pathlib import Path

from codegen.cli.commands.init.main import init_command


def test_init_command_success(isolated_cli_runner):
    """Test successful initialization of a new codegen project"""
    # Set up a git repo in the isolated filesystem
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)

    # Run the command
    result = isolated_cli_runner.invoke(init_command, ["--organization-name", "test-org", "--repo-name", "test-repo"])

    # Assertions
    assert result.exit_code == 0

    # Check that the .codegen directory was created with expected structure
    codegen_dir = Path(".codegen")
    assert codegen_dir.exists()
    assert codegen_dir.is_dir()

    # Check that config file exists
    config_file = codegen_dir / "config.json"
    assert config_file.exists()
    assert config_file.is_file()


def test_init_command_update_existing(isolated_cli_runner):
    """Test updating an existing codegen project"""
    # First create a git repo and initial codegen setup
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)

    # Initial init
    result = isolated_cli_runner.invoke(init_command, ["--organization-name", "test-org", "--repo-name", "test-repo"])
    assert result.exit_code == 0

    # Get initial modification time
    config_file = Path(".codegen/config.json")
    initial_mtime = config_file.stat().st_mtime

    # Run update
    result = isolated_cli_runner.invoke(init_command, ["--organization-name", "updated-org"])

    # Assertions
    assert result.exit_code == 0
    assert config_file.stat().st_mtime > initial_mtime  # File was updated


def test_init_command_not_git_repo(isolated_cli_runner):
    """Test initialization failure when not in a git repository"""
    result = isolated_cli_runner.invoke(init_command)

    assert result.exit_code == 1
    assert "Not in a git repository" in result.output


def test_init_command_infer_git_info(isolated_cli_runner):
    """Test init command inferring organization and repo from git"""
    # Set up git repo with a remote
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)
    subprocess.run(["git", "remote", "add", "origin", "git@github.com:test-org/test-repo.git"], check=True)

    result = isolated_cli_runner.invoke(init_command)

    assert result.exit_code == 0

    # Verify the config contains inferred values
    config_file = Path(".codegen/config.json")
    assert config_file.exists()
    assert "test-org" in config_file.read_text()
    assert "test-repo" in config_file.read_text()
