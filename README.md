# Codegen CLI

A command-line interface for the Codegen API.

## Installation

To install for development run:

```
pip install -e .
```


## Installation in Devin
```bash
pyenv install 3.13.0
pyenv global 3.13.0 # This sets Python 3.13 as the default version
pip install uv
uv tool install keyring --with keyrings.codeartifact --reinstall
uv venv # Creates venv using the Python version set by pyenv
source .venv/bin/activate
uv pip install codegen-sh
# uv pip install --upgrade codegen-sh # to update to latest version
```