from argparse import Namespace
from pathlib import Path

from dotenv import load_dotenv

from psenv import aws
from psenv.core import fileio, models


class Context:
    def __init__(self, env: str, config: Path) -> None:
        # Load the configuration file and get the environment configuration
        self.config = models.load_config(config)
        self.config_env = self.config.get_config_environment(env)

        # Load environment variables from the .env file specified in the config
        load_dotenv(self.config.envfile)

        # Check the sts account to ensure we are in the expected AWS account
        self.sts = aws.StsClient()
        self.sts.raise_if_invalid_account(self.config_env.environment.account)

        # Load the environment file and its parameters we are using for this context
        self.env_file = fileio.EnvFile(Path(self.config_env.environment.envfile))
        self.env_file.load()

        # Initialize the Parameter Store client with the parameter path and KMS key from the config
        self.ps_client = aws.ParameterStoreClient(parameter_path=self.config_env.parameter_path, kms_key=self.config_env.kms_key)

    @classmethod
    def from_cliargs(cls, cliargs: Namespace) -> "Context":
        """Create a Context instance from command line arguments."""
        return cls(env=cliargs.env, config=cliargs.config)
