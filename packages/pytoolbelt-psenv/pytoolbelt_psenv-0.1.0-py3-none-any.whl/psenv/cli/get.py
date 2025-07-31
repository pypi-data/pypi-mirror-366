from argparse import Namespace
from typing import Any

import structlog

from psenv.core.context import Context

logger = structlog.get_logger(__name__)


def configure_parser(subparser: Any) -> None:
    get_parser = subparser.add_parser(
        name="get", description="Manage psenv configurations.", help="Get parameters from the parameter store."
    )
    get_parser.set_defaults(func=get_parameters)

    get_parser.add_argument(
        "-e",
        "--env",
        type=str,
        required=True,
    )


def get_parameters(cliargs: Namespace) -> int:
    logger.info("Fetching parameters from parameter store.", config=cliargs.config)

    ctx = Context.from_cliargs(cliargs)

    # Fetch parameters from the parameter store
    parameters = ctx.ps_client.get_parameters()

    # write them to the configured env file
    ctx.env_file.update_params(parameters, "main")
    ctx.env_file.write_params()
    return 0
