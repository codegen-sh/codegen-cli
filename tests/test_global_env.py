import os

import pytest

from codegen.env.enums import Environment
from codegen.env.global_env import GlobalEnv


@pytest.mark.parametrize(
    "env_envvar,expected_env",
    [
        ("", Environment.STAGING),
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
    del os.environ["ENV"]
    global_env = GlobalEnv()
    assert global_env.ENV == Environment.STAGING


def test_global_env_parse_env_bad_value_raises():
    os.environ["ENV"] = "bad_value"
    with pytest.raises(ValueError) as exc_info:
        global_env = GlobalEnv()
    assert "Invalid environment: bad_value" in str(exc_info.value)
