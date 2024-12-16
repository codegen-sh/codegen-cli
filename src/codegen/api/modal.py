from codegen.env.enums import Environment
from codegen.env.global_env import global_env


def get_modal_workspace():
    match global_env.ENV:
        case Environment.PRODUCTION:
            return "codegen-sh"
        case Environment.STAGING:
            return "codegen-sh-staging"
        case Environment.DEVELOP:
            return "codegen-sh-develop"
        case _:
            raise ValueError(f"Invalid environment: {global_env.ENV}")


MODAL_WORKSPACE = get_modal_workspace()
