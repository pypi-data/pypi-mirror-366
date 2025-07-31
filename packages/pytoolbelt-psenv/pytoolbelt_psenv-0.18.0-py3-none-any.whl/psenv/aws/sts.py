from typing import Optional

import boto3
from mypy_boto3_sts import STSClient
from mypy_boto3_sts.type_defs import GetCallerIdentityResponseTypeDef

from psenv.error_handling.exceptions import PsenvInternalError, PsenvInvalidAccountError


class StsClient:
    def __init__(self, sts_client: Optional[STSClient] = None) -> None:
        self._sts = sts_client or boto3.client("sts")
        self._caller_identity: Optional[GetCallerIdentityResponseTypeDef] = None

    @property
    def sts(self) -> STSClient:
        return self._sts

    @property
    def caller_identity(self) -> GetCallerIdentityResponseTypeDef:
        if not self._caller_identity:
            self._caller_identity = self.get_caller_identity()
        return self._caller_identity

    @property
    def account_id(self) -> str:
        return self.caller_identity.get("Account", "")

    def get_caller_identity(self) -> GetCallerIdentityResponseTypeDef:
        try:
            return self.sts.get_caller_identity()
        except Exception as e:
            raise PsenvInternalError(f"Failed to get caller identity: {e}") from e

    def raise_if_invalid_account(self, expected_account_id: str) -> None:
        if self.account_id != expected_account_id:
            raise PsenvInvalidAccountError(f"Invalid AWS account ID: {self.account_id}. Expected: {expected_account_id}.")
