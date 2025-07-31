# psenv

psenv is a CLI tool for managing environment variables using AWS Parameter Store. It allows you to fetch, inject, and sync environment variables for your projects, making it easy to manage secrets and configuration across different projects.

## Key Features
- Fetch environment variables from AWS Parameter Store
- Inject variables into your shell or process
- Sync variables to and from .env files

## Example Workflow

### 1. Onboarding a New Developer
A new developer can fetch environment variables for their environment using:

```sh
psenv get --env dev
```

This will create a `.env` file in the configured directory with the following content:

```dotenv
SOME_VARIABLE1=123
SOME_VARIABLE2=234

#<private>
GITHUB_TOKEN=<REPLACE-WITH-YOUR-PERSONAL-GH-TOKEN>
```

Variables under the `#<private>` section are user-specific and should be set by each developer. These are not shared between users.

## Command Reference

- `psenv get --env <env>`: Fetches environment variables for the specified environment.
- `psenv inject --env <env>`: Injects environment variables from your shell into a .env file.
- `psenv put --env <env> --sync`: Syncs your local .env file to the parameter store.
- `psenv put --env <env> --add`: Adds new parameters from your .env file to the parameter store.
- `psenv put --env <env> --update`: Adds new and updates existing parameters in the parameter store from your .env file.
- `psenv put --env <env> --dry-run --sync`: Shows what would be changed without making any modifications.

## Notes
- You do not need a `.env` file to run commands with parameters; values are pulled directly from the parameter store.
- `.env` files can be used for syncing environments, as well as used locally for development. Ideally .env files are not kept locally long term and the `psenv exec --env <env>` command is used to inject variables form the parameter store at runtime.
- The `#<private>` section in the `.env` file is for user-specific / developer secrets
  and should not be shared between developers.
- No variables in the `#<private>` section will be synced to the parameter store.
- NEVER commit your `.env` file to version control, as it may contain sensitive information.

## See Also
- [psenv.yml documentation](docs/usage/configuration.md)
- [Command reference](docs/usage/commands.md)
