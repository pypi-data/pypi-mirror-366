from pathlib import Path

PSENV_FILE_NAME = "psenv.yml"
PSENV_CONFIG_FILE_PATH = Path.cwd() / PSENV_FILE_NAME
PSENV_TEMPLATE_FILE_PATH = Path(__file__).parent.parent / "templates" / "psenv.template.yml"
