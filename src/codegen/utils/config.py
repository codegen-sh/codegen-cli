from pathlib import Path

import toml
from pydantic import BaseModel


class AnalyticsConfig(BaseModel):
    telemetry_enabled: bool = True
    distinct_id: str = ""


class Config(BaseModel):
    repo_name: str = ""
    organization_name: str = ""
    programming_language: str | None = None
    analytics: AnalyticsConfig = AnalyticsConfig()

    @property
    def repo_full_name(self) -> str:
        return f"{self.organization_name}/{self.repo_name}"


class State(BaseModel):
    active_codemod: str = ""


STATE_PATH = "state.toml"
CONFIG_PATH = "config.toml"


def read_model[T: BaseModel](model: type[T], path: Path) -> T:
    if not path.exists():
        return model()
    return model.model_validate(toml.load(path))


def get_config(codegen_dir: Path) -> Config:
    config_path = codegen_dir / CONFIG_PATH
    return read_model(Config, config_path)


def get_state(codegen_dir: Path) -> State:
    state_path = codegen_dir / STATE_PATH
    return read_model(State, state_path)


def write_model(model: BaseModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        toml.dump(model.model_dump(), f)


def write_config(config: Config, codegen_dir: Path) -> None:
    config_path = codegen_dir / CONFIG_PATH
    write_model(config, config_path)


def write_state(state: State, codegen_dir: Path) -> None:
    state_path = codegen_dir / STATE_PATH
    write_model(state, state_path)
