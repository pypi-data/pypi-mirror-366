from argparse import Action, Namespace
from pathlib import Path
from typing import Any

import structlog

from psenv.core import fileio
from psenv.core.paths import PSENV_CONFIG_FILE_PATH
from psenv.error_handling.exceptions import PsenvConfigError

logger = structlog.get_logger(__name__)


class ValidatePathAction(Action):
    def __call__(self, parser, namespace, values: Path, option_string=None):
        if not values.suffix:
            raise PsenvConfigError(f"Path is not a file: {values}")
        if not values.suffix == ".yml":
            raise PsenvConfigError(f"Invalid file type: {values.suffix}. Expected a .yml file.")
        if values.exists():
            raise PsenvConfigError(f"Psenv config file already exists: {values}")
        setattr(namespace, self.dest, values)


def configure_parser(subparser: Any) -> None:
    config_parser = subparser.add_parser(name="config", description="Manage psenv configurations.")

    subparser = config_parser.add_subparsers(dest="new_config")
    new_parser = subparser.add_parser(name="new", description="Create a new psenv configuration file.")
    new_parser.set_defaults(func=new_config)
    new_parser.add_argument(
        "-p",
        "--path",
        help="Path to the new configuration file.",
        type=Path,
        required=False,
        default=PSENV_CONFIG_FILE_PATH,
        action=ValidatePathAction,
    )


def new_config(cliargs: Namespace) -> int:
    logger.info("Creating new psenv configuration file", path=cliargs.path)
    template = fileio.read_config_template()
    fileio.write_config(cliargs.path, template)
    return 0
