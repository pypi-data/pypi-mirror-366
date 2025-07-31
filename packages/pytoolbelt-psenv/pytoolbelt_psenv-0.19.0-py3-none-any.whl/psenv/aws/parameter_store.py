from typing import Any, Dict, Iterable, Optional, Tuple

import boto3
import structlog
from mypy_boto3_ssm import SSMClient

from psenv.error_handling.exceptions import PsenvParameterStoreError


class ParameterStoreClient:
    def __init__(self, parameter_path: str, ssm_client: Optional[SSMClient] = None, kms_key: Optional[str] = None) -> None:
        self._parameter_path = parameter_path
        self._ssm = ssm_client or boto3.client("ssm")
        self._kms_key = kms_key
        self.logger = structlog.getLogger("psenv.parameter_store")

    @property
    def ssm(self) -> SSMClient:
        return self._ssm

    @property
    def parameter_path(self) -> str:
        return self._parameter_path

    @property
    def kms_key(self) -> str:
        return self._kms_key or "alias/aws/ssm"

    @property
    def get_params_kwargs(self) -> Dict[str, Any]:
        return {
            "Path": self.parameter_path,
            "Recursive": True,
            "WithDecryption": True,
        }

    def put_params_kwargs(self, name: str, value: str, overwrite: bool) -> Dict[str, Any]:
        return {
            "Name": f"{self.parameter_path}/{name}",
            "Value": value,
            "Type": "SecureString",
            "Overwrite": overwrite,
            "KeyId": self.kms_key,
        }

    @staticmethod
    def parse_parameter_name(name: str) -> str:
        return name.split("/")[-1].upper()

    def _get_parameters(self) -> Iterable[Tuple[str, str]]:
        paginator = self.ssm.get_paginator("get_parameters_by_path")
        try:
            for page in paginator.paginate(**self.get_params_kwargs):
                for parameter in page.get("Parameters", []):
                    name = self.parse_parameter_name(parameter["Name"])
                    yield name, parameter["Value"]
        except Exception as e:
            raise PsenvParameterStoreError(f"Error fetching parameters {e}") from e

    def get_parameters(self) -> Dict[str, str]:
        return dict(self._get_parameters())

    def put_parameters(self, parameters: Dict[str, str], overwrite: bool = False) -> None:
        for name, value in parameters.items():
            try:
                self.logger.info("Putting parameter", name=f"{self.parameter_path}/{name}", overwrite=overwrite)
                self.ssm.put_parameter(**self.put_params_kwargs(name, value, overwrite))
            except Exception as e:
                raise PsenvParameterStoreError(f"Error putting Parameters: {e}") from e

    def delete_parameters(self, parameters: Dict[str, str]) -> None:
        for name in parameters:
            try:
                self.logger.info("Deleting parameter", name=f"{self.parameter_path}/{name}")
                self.ssm.delete_parameter(Name=f"{self.parameter_path}/{name}")
            except Exception as e:
                raise PsenvParameterStoreError(f"Error deleting parameter {name}: {e}") from e
