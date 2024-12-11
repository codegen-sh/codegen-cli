from codegen.env import ENV


def get_modal_workspace():
    match ENV:
        case "production":
            return "codegen-sh"
        case "staging":
            return "codegen-sh-staging"
        case "develop":
            return "codegen-sh-develop"
        case _:
            raise ValueError(f"Invalid environment: {ENV}")
