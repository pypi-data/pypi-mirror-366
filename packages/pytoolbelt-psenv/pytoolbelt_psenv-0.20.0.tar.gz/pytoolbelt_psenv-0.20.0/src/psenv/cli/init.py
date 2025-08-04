from argparse import Namespace
from typing import Any

import structlog

from psenv.core import fileio

logger = structlog.get_logger(__name__)


def configure_parser(subparser: Any) -> None:
    init_parser = subparser.add_parser(name="init", help="Initialize a psenv project", description="Manage psenv configurations.")
    init_parser.set_defaults(func=init_entrypoint)


def init_entrypoint(cliargs: Namespace) -> None:
    logger.info("Creating new psenv configuration file")
    template = fileio.read_config_template()
    fileio.write_config(cliargs.config, template)

    logger.info("Creating new psenv environment directory")
    default_env = fileio.DefaultEnvPaths(cliargs.config)
    default_env.create()
