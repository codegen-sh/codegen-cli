import os
from enum import StrEnum

from dotenv import load_dotenv

# NOTE: load_dotenv here to ensure it's loaded before ENV is accessed
load_dotenv()


class Environment(StrEnum):
    PRODUCTION = "prod"
    STAGING = "staging"
    DEVELOP = "develop"


DEFAULT_ENV = Environment.STAGING
ENV = os.environ.get("ENV", DEFAULT_ENV)
