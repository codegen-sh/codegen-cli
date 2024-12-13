import os
from enum import StrEnum

from dotenv import load_dotenv

load_dotenv()


class Environment(StrEnum):
    PRODUCTION = "prod"
    STAGING = "staging"
    DEVELOP = "develop"


DEFAULT_ENV = Environment.STAGING
ENV = os.environ.get("ENV", DEFAULT_ENV)
