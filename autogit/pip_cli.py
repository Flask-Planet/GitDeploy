import subprocess
from pathlib import Path
from typing import Optional


class PipCli:

    def __init__(self, command: str = "", cwd: Optional[Path] = None):
        self.process = None
        self.command = command.split(" ")
        self.cwd = cwd or Path.cwd()

    def __enter__(self) -> str:
        try:
            self.process = subprocess.Popen(
                [f"{self.cwd}/venv/bin/pip", *self.command],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd,
            )
        except Exception as e:
            return f"Error: {e}"

        self.process.stdin.close()

        return self.process.stdout.read().decode()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.process:
            self.process.terminate()
