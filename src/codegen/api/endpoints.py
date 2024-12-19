from codegen.env.global_env import global_env

RUN_ENDPOINT = f"https://{global_env.MODAL_WORKSPACE}--cli-run.modal.run"
DOCS_ENDPOINT = f"https://{global_env.MODAL_WORKSPACE}--cli-docs.modal.run"
EXPERT_ENDPOINT = f"https://{global_env.MODAL_WORKSPACE}--cli-ask-expert.modal.run"
IDENTIFY_ENDPOINT = f"https://{global_env.MODAL_WORKSPACE}--cli-identify.modal.run"
CREATE_ENDPOINT = f"https://{global_env.MODAL_WORKSPACE}--cli-create.modal.run"
