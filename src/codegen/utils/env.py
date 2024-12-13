import os
from enum import StrEnum


class Environment(StrEnum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOP = "develop"


DEFAULT_ENV = Environment.STAGING.value
ENV = os.environ.get("ENV", DEFAULT_ENV)
