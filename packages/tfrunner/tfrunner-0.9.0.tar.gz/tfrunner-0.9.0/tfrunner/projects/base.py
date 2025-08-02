from enum import Enum
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel

from tfrunner.secrets_backend.base import SecretsBackendKind
from tfrunner.state_backend.base import StateBackendKind


class SecretsBackendConfig(BaseModel):
    kind: SecretsBackendKind
    spec: dict


class StateBackendConfig(BaseModel):
    kind: StateBackendKind
    spec: dict


class ProjectConfig(BaseModel):
    path: Path
    state_name: str
    secrets_backend: SecretsBackendConfig | None = None
    env: dict[str, str] | None = None


class TfrunnerFlavour(str, Enum):
    TOFU = "tofu"
    TERRAFORM = "terraform"


class TfrunnerConfig(BaseModel):
    flavour: TfrunnerFlavour
    state_backend: StateBackendConfig
    secrets_backend: SecretsBackendConfig | None = None
    projects: dict[str, ProjectConfig]
    env: dict[str, str] | None = None

    @classmethod
    def from_yaml(cls, config_path: Path) -> Self:
        with open(config_path, "r") as f:
            config: dict = yaml.safe_load(f)
        config = TfrunnerConfig(**config)
        config.state_backend.spec["flavour"] = config.flavour.value
        return config
