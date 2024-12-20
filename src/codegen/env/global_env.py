import os

from dotenv import load_dotenv

from codegen.env.constants import DEFAULT_ENV
from codegen.env.enums import Environment


class GlobalEnv:
    def __init__(self) -> None:
        load_dotenv()

        self.ENV = self._parse_env()

        # =====[ DEV ]=====
        self.DEBUG = self._get_env_var("DEBUG")

        # =====[ AUTH ]=====
        self.CODEGEN_USER_ACCESS_TOKEN = self._get_env_var("CODEGEN_USER_ACCESS_TOKEN")

        # =====[ ALGOLIA ]=====
        self.ALGOLIA_SEARCH_KEY = self._get_env_var("ALGOLIA_SEARCH_KEY")

        # =====[ POSTHOG ]=====
        self.POSTHOG_PROJECT_API_KEY = self._get_env_var("POSTHOG_PROJECT_API_KEY")
        self.POSTHOG_API_KEY = self._get_env_var("POSTHOG_API_KEY")

        # =====[ MODAL ]=====
        self.MODAL_ENVIRONMENT = self._get_env_var("MODAL_ENVIRONMENT")

    def _get_env_var(self, var_name, required: bool = False) -> str:
        if self.ENV == "local":
            return ""

        value = os.environ.get(var_name)
        if value:
            return value
        if required:
            raise ValueError(f"Environment variable {var_name} is not set with ENV={self.ENV}!")
        return ""

    def _parse_env(self) -> Environment:
        envvar = os.environ.get("ENV")

        if not envvar:
            return DEFAULT_ENV
        if envvar not in Environment:
            raise ValueError(f"Invalid environment: {envvar}")
        return Environment(envvar)


# NOTE: load and store envvars once
global_env = GlobalEnv()
