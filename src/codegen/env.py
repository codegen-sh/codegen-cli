import os

from codegen.modal import get_modal_workspace


DEFAULT_ENV = "staging"
ENV = os.environ.get("ENV", DEFAULT_ENV)
MODAL_WORKSPACE = get_modal_workspace()
