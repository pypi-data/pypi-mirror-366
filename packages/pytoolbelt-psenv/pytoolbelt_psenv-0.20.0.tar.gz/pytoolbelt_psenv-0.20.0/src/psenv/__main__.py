from psenv.cli import parse_args
from psenv.error_handling import handle_cli_errors


@handle_cli_errors
def main() -> int:
    cliargs = parse_args()
    return cliargs.func(cliargs=cliargs)


if __name__ == "__main__":
    exit(main())
