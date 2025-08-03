from argparse import Namespace
from typing import Any

import structlog

from psenv.core import diff
from psenv.core.context import Context
from psenv.core.synchronizer import Synchronizer

logger = structlog.get_logger(__name__)


def configure_parser(subparser: Any) -> None:
    put_parser = subparser.add_parser(
        name="put", description="Manage psenv configurations.", help="Put parameters into the parameter store."
    )
    put_parser.set_defaults(func=put_parameters)

    put_parser.add_argument("-e", "--env", type=str, required=True, help="The environment to put parameters for.", metavar="")

    group = put_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--add", action="store_true", help="Add new parameters only.")
    group.add_argument("-u", "--update", action="store_true", help="Add new and update existing parameters.")
    group.add_argument(
        "-s", "--sync", action="store_true", help="Add new, update existing, and remove parameters not in the local environment file."
    )

    put_parser.add_argument("--dry-run", action="store_true", help="Show what would be done, but do not make any changes.")


def put_parameters(cliargs: Namespace) -> None:
    logger.info("Putting parameters into the parameter store for environment:", config=cliargs.config)

    ctx = Context.from_cliargs(cliargs)

    # fetch the remote parameters from the parameter store
    remote_params = ctx.ps_client.get_parameters()

    # generate a parameter diff to use for the put operation
    param_diff = diff.diff_parameters(ctx.env_file.local_params, remote_params)

    # get the synchronizer
    synchronizer = Synchronizer(ctx=ctx, param_diff=param_diff, mode=Synchronizer.get_mode_from_cliargs(cliargs), dry_run=cliargs.dry_run)
    # execute the synchronization
    synchronizer.sync()
