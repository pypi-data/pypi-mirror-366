import functools
from typing import Callable, Optional

import structlog

from psenv.core import config

from . import exceptions


class ErrorHandler:
    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name
        self.raise_errors = config.PSENV_RAISE_ERRORS
        self.logger = structlog.get_logger(name or self.__class__.__name__)

    def handle(self, exception: Exception) -> int:
        if self.raise_errors:
            raise exception
        self.logger.error(exception)
        return 1


def handle_cli_errors(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> int:
        error_handler = ErrorHandler()

        try:
            return func(*args, **kwargs)

        except exceptions.PsenvParameterStoreError as e:
            return error_handler.handle(e)

        except exceptions.PsenvConfigNotFoundError as e:
            return error_handler.handle(e)

        except exceptions.PsenvConfigError as e:
            return error_handler.handle(e)

    return wrapper
