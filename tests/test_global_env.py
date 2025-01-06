import os
from pathlib import Path

import pytest

from codegen.env.enums import Environment
from codegen.env.global_env import GlobalEnv


@pytest.mark.parametrize(
    "env_envvar,expected_env",
    [
        ("", Environment.PRODUCTION),
        ("develop", Environment.DEVELOP),
        ("staging", Environment.STAGING),
        ("prod", Environment.PRODUCTION),
    ],
)
def test_global_env_parse_env_expected(env_envvar: str | None, expected_env: Environment):
    os.environ["ENV"] = env_envvar
    global_env = GlobalEnv()
    assert global_env.ENV == expected_env


def test_global_env_parse_env_env_unset():
    if "ENV" in os.environ:
        del os.environ["ENV"]
    global_env = GlobalEnv()
    assert global_env.ENV == Environment.PRODUCTION


def test_global_env_parse_env_bad_value_raises():
    os.environ["ENV"] = "bad_value"
    with pytest.raises(ValueError) as exc_info:
        global_env = GlobalEnv()
    assert "Invalid environment: bad_value" in str(exc_info.value)


def test_global_env_load_dotenv_env_specific_file_exists():
    os.environ["ENV"] = "develop"
    env_file = Path(".env.develop")

    try:
        env_file.write_text("MODAL_ENVIRONMENT=codegen")
        global_env = GlobalEnv()
        assert global_env.MODAL_ENVIRONMENT == "codegen"
    finally:
        env_file.unlink()


def test_global_env_load_dotenv_env_specific_file_does_not_exist():
    os.environ["ENV"] = "develop"
    env_file = Path(".env")
    env_file.write_text("MODAL_ENVIRONMENT=bot")
    try:
        global_env = GlobalEnv()
        assert global_env.MODAL_ENVIRONMENT == "bot"
    finally:
        env_file.unlink()
