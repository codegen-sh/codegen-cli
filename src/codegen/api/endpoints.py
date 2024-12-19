from codegen.env.global_env import global_env

modal_workspace = global_env.MODAL_WORKSPACE
RUN_ENDPOINT = f"https://{modal_workspace}--cli-run.modal.run"
DOCS_ENDPOINT = f"https://{modal_workspace}--cli-docs.modal.run"
EXPERT_ENDPOINT = f"https://{modal_workspace}--cli-ask-expert.modal.run"
IDENTIFY_ENDPOINT = f"https://{modal_workspace}--cli-identify.modal.run"
CREATE_ENDPOINT = f"https://{modal_workspace}--cli-create.modal.run"
