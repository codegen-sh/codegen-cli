from pathlib import Path

import toml
from pydantic import BaseModel


class AnalyticsConfig(BaseModel):
    telemetry_enabled: bool = True
    distinct_id: str = ""


class Config(BaseModel):
    repo_name: str = ""
    organization_name: str = ""
    analytics: AnalyticsConfig = AnalyticsConfig()

    @property
    def repo_full_name(self) -> str:
        return f"{self.organization_name}/{self.repo_name}"


class State(BaseModel):
    active_codemod: str = ""


STATE_PATH = "state.toml"
CONFIG_PATH = "config.toml"


def get_config(codegen_dir: Path) -> Config:
    config_path = codegen_dir / CONFIG_PATH
    if not config_path.exists():
        return Config(repo_name="", organization_name="")
    return Config.model_validate(toml.load(config_path))


def get_state(codegen_dir: Path) -> State:
    state_path = codegen_dir / STATE_PATH
    if not state_path.exists():
        return State(active_codemod="")
    return State.model_validate(toml.load(state_path))


def write_config(config: Config, codegen_dir: Path) -> None:
    config_path = codegen_dir / CONFIG_PATH
    with config_path.open("w") as f:
        toml.dump(config.model_dump(), f)


def write_state(state: State, codegen_dir: Path) -> None:
    state_path = codegen_dir / STATE_PATH
    with state_path.open("w") as f:
        toml.dump(state.model_dump(), f)
