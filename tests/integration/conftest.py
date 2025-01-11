import pytest
from click.testing import CliRunner


@pytest.fixture
def isolated_cli_runner():
    """Fixture that provides an isolated CLI runner with temp directory"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner
