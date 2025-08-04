import os
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional, TextIO

import yaml
from dotenv import dotenv_values

from psenv.core.config import PSENV_PRIVATE_MARKER
from psenv.core.paths import PSENV_CONFIG_FILE_PATH, PSENV_TEMPLATE_FILE_PATH
from psenv.error_handling.exceptions import PsenvConfigError, PsenvConfigNotFoundError, PsenvInternalError


def read_config(path: Path) -> Dict[str, Any]:
    path = path.absolute()
    try:
        content = os.path.expandvars(path.read_text())
        return yaml.safe_load(content)
    except FileNotFoundError:
        raise PsenvConfigNotFoundError(
            f"psenv.yml not found in {path.as_posix()}. Please check the path or create a new configuration file."
        )
    except yaml.YAMLError as e:
        raise PsenvConfigError("Error loading psenv.yml") from e


def read_config_template(path: Optional[Path] = None) -> str:
    path = path or PSENV_TEMPLATE_FILE_PATH
    try:
        return path.absolute().read_text()
    except FileNotFoundError:
        raise PsenvInternalError(f"psenv template file not found at {path}. Please file a bug report.")


def write_config(path: Path, content: str) -> None:
    path = path.absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    path.write_text(content)


def get_environment_variables(prefix: str) -> Dict[str, str]:
    retrieved = {}
    prefix = prefix.upper()
    for key, value in os.environ.items():
        if key.startswith(prefix):
            retrieved[key] = value
    return retrieved


class EnvFile:
    def __init__(self, path: Path) -> None:
        self.path = path.expanduser().absolute()
        self._main_params = {}
        self._private_params = {}

        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch(exist_ok=True)

    @property
    def local_params(self) -> Dict[str, str]:
        return self._main_params

    @staticmethod
    def _split_sections(content: str) -> tuple[str, str]:
        mp, _, pp = content.partition(PSENV_PRIVATE_MARKER)
        return mp, pp

    @staticmethod
    def _parse_env_section(section: str) -> Dict[str, str]:
        with StringIO() as stream:
            stream.write(section)
            stream.seek(0)
            return dotenv_values(stream=stream)

    @staticmethod
    def _get_prefix(key: str) -> str:
        return key.split("_")[0]

    @staticmethod
    def _write_section_params(params: Dict[str, str], env: TextIO) -> None:
        last_prefix = None
        for key in sorted(params.keys()):
            prefix = EnvFile._get_prefix(key)
            if prefix != last_prefix:
                env.write("\n")
                env.write(f"# ----------------------------{prefix}------------------------------------ #\n")
                last_prefix = prefix
            env.write(f"{key}='{params[key]}'\n")

    def load(self) -> None:
        content = self.path.read_text()
        mp, pp = self._split_sections(content)
        self._main_params = self._parse_env_section(mp)
        self._private_params = self._parse_env_section(pp)

    def get_params(self, section: str) -> Dict[str, str]:
        return getattr(self, f"_{section}_params", {})

    def update_params(self, params: Dict[str, str], section: str) -> None:
        p = self.get_params(section)
        p.update(**params)
        setattr(self, f"_{section}_params", p)

    def write_params(self) -> None:
        with self.path.open(mode="w+") as env:
            self._write_section_params(self._main_params, env)
            env.write(f"\n\n{PSENV_PRIVATE_MARKER}\n\n")
            self._write_section_params(self._private_params, env)


class DefaultEnvPaths:
    def __init__(self, path: Path) -> None:
        if path == PSENV_CONFIG_FILE_PATH:
            path = path.parent
        self.path = path

    @property
    def environment_directory(self) -> Path:
        return self.path / "environments"

    @property
    def production_env_file(self) -> Path:
        return self.environment_directory / "prd.env"

    @property
    def development_env_file(self) -> Path:
        return self.environment_directory / "dev.env"

    @property
    def testing_env_file(self) -> Path:
        return self.environment_directory / "test.env"

    def create(self) -> None:
        self.environment_directory.mkdir(parents=True, exist_ok=True)

        if not self.production_env_file.exists():
            self.production_env_file.touch()

        if not self.development_env_file.exists():
            self.development_env_file.touch()

        if not self.testing_env_file.exists():
            self.testing_env_file.touch()
