import os
from subprocess import PIPE, Popen
from typing import Dict, List, Optional


class Command(Popen):
    def __init__(self, command: List[str], env: Optional[Dict[str, str]] = None) -> None:
        if command[0] == "--":
            command.pop(0)

        super().__init__(
            command,
            env=env or os.environ.copy(),  # Use provided env or inherit from parent
            stdout=None,  # None means inherit from parent process
            stderr=PIPE,  # Capture stderr for error checking
            text=True,  # Return strings instead of bytes
            bufsize=1,  # Line buffered
            universal_newlines=True,
        )
        self.command = command
        self.env = env

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Get stderr output and return code
        stderr = self.stderr.read() if self.stderr else ""
        return_code = self.wait()

        if return_code != 0:
            self.stderr.close()
            raise RuntimeError(f"Command failed with code {return_code}. Error: {stderr}")

        self.stderr.close()
        return False  # Don't suppress exceptions
