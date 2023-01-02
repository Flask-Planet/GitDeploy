import subprocess
from dataclasses import dataclass
from pathlib import Path

from .resources import Resources


@dataclass
class SupervisorIni:
    path: Path
    app: str
    working_directory: str
    command: str
    autostart: bool
    autorestart: bool
    log_location: str

    def __str__(self):
        return Resources.supervisor_ini.format(
            app=self.app,
            working_directory=self.working_directory,
            command=self.command,
            autostart="true" if self.autostart else "false",
            autorestart="true" if self.autorestart else "false",
            log_location=self.log_location,
        )


class Supervisor:
    supervisor_config: Path
    config_includes_path: Path

    def __init__(
            self,
            supervisor_config: str,
            config_includes_path: str
    ):
        self.supervisor_config = Path(supervisor_config)
        self.config_includes_path = Path(config_includes_path)

    def setup(self):
        if not self.supervisor_config.exists():
            raise FileNotFoundError(
                f"Supervisor config file not found at {self.supervisor_config}"
            )

        if not self.config_includes_path.exists():
            raise FileNotFoundError(
                f"Supervisor config includes path not found at {self.config_includes_path}"
            )

        with open(self.supervisor_config, "w") as f:
            f.write(
                Resources.supervisor_config.format(
                    config_includes_path=self.config_includes_path
                )
            )

    def write_init(self, ini: SupervisorIni):
        with open(self.config_includes_path / f"{ini.app}.ini", "w") as f:
            f.write(str(ini))


class SupervisorctlController:

    def __init__(self, command_group: list[str]):
        self.process = None
        self.command_group = command_group

    def __enter__(self) -> list[str]:
        self.process = subprocess.Popen(
            ["supervisorctl"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        for command in self.command_group:
            self.process.stdin.write(f"{command}\n".encode())

        self.process.stdin.write(f"exit\n".encode())
        self.process.stdin.close()

        _ = []
        for line in self.process.stdout.read().decode().split("\n"):
            _.append(line.replace("supervisor> ", ""))

        return list(filter(None, _))

    def __exit__(self, exc_type, exc_value, traceback):
        if self.process:
            self.process.terminate()
