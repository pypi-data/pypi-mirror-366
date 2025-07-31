import os


def get_raise_errors_env():
    return os.getenv("PSENV_RAISE_ERRORS", "false").lower() == "true"


PSENV_RAISE_ERRORS = get_raise_errors_env()
PSENV_PRIVATE_MARKER = "#<private>"
