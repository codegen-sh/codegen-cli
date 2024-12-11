import os

DEFAULT_ENV = "staging"
ENV = os.environ.get("ENV", DEFAULT_ENV)
