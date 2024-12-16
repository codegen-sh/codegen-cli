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


def get_config(codegen_dir: Path) -> Config:
    config_path = codegen_dir / "config.toml"
    if not config_path.exists():
        return Config(repo_name="", organization_name="")
    return Config.model_validate(toml.load(config_path))


def write_config(config: Config, codegen_dir: Path) -> None:
    config_path = codegen_dir / "config.toml"
    with config_path.open("w") as f:
        toml.dump(config.model_dump(), f)
