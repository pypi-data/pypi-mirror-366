from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, ValidationError, field_validator

from psenv.core.fileio import read_config
from psenv.core.paths import PSENV_CONFIG_FILE_PATH
from psenv.error_handling.exceptions import PsenvConfigError


class Environment(BaseModel):
    name: str
    account: str
    envfile: str
    kms_key: Optional[str] = None
    path: Optional[str] = None

    @field_validator("account")
    def validate_account(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 12:
            raise PsenvConfigError("AWS account ID must be a 12-digit numeric string.")
        return value

    @field_validator("path")
    def validate_path(cls, value: Optional[str]) -> Optional[str]:
        if value and not value.startswith("/"):
            raise PsenvConfigError("Path must start with '/'.")
        return value

    @field_validator("kms_key")
    def validate_kms_key(cls, value: Optional[str]) -> Optional[str]:
        if value and not value.startswith("alias/"):
            raise PsenvConfigError("KMS key must start with 'alias/'.")
        return value


class PsenvConfig(BaseModel):
    envfile: str
    root_path: str
    root_kms_key: Optional[str] = None
    environments: List[Environment]

    @field_validator("root_path")
    def validate_path(cls, value: str) -> Optional[str]:
        if not value.startswith("/"):
            raise PsenvConfigError("Path must start with '/'.")
        return value

    @field_validator("root_kms_key")
    def validate_kms_key(cls, value: Optional[str]) -> Optional[str]:
        if value and not value.startswith("alias/"):
            raise PsenvConfigError("KMS key must start with 'alias/'.")
        return value

    def get_config_environment(self, name: str) -> "ConfigEnvironment":
        for env in self.environments:
            if env.name == name:
                return ConfigEnvironment(config=self, environment=env)
        raise PsenvConfigError(f"Environment '{name}' not found in configuration.")


class ConfigEnvironment(BaseModel):
    config: PsenvConfig
    environment: Environment

    @property
    def parameter_path(self) -> str:
        if self.environment.path:
            return f"{self.config.root_path}/{self.environment.name}{self.environment.path}"
        return self.config.root_path

    @property
    def kms_key(self) -> Optional[str]:
        return self.environment.kms_key or self.config.root_kms_key


def load_config(path: Optional[Path] = None) -> PsenvConfig:
    path = path or PSENV_CONFIG_FILE_PATH
    config = read_config(path)
    try:
        return PsenvConfig.model_validate(config)
    except (ValidationError, AssertionError, PsenvConfigError) as e:
        raise PsenvConfigError(f"Error loading config {e}")
