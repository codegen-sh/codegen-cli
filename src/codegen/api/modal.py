from codegen.utils.env import ENV, Environment


def get_modal_workspace():
    match ENV:
        case Environment.PRODUCTION:
            return "codegen-sh"
        case Environment.STAGING:
            return "codegen-sh-staging"
        case Environment.DEVELOP:
            return "codegen-sh-develop"
        case _:
            raise ValueError(f"Invalid environment: {ENV}")


MODAL_WORKSPACE = get_modal_workspace()
