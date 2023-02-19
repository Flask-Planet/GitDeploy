import json
import os
import sys
import typing as t
from pathlib import Path

try:
    from resources import Resources
    from terminator import Terminator
except ModuleNotFoundError:
    from gitdeployflask.resources import Resources
    from gitdeployflask.terminator import Terminator


def _process_os_release(terminal_output: list):
    distro = None
    version = None
    for line in terminal_output:
        if "PRETTY_NAME" in line:
            value = line.replace('"', '').split("=")[1]
            distro = value.split(" ")[0].lower()
        if "VERSION_ID" in line:
            value = line.replace('"', '').split("=")[1]
            version = value
        if "ProductName" in line:
            value = line.replace('\t', '').split(":")[1]
            distro = value.lower()
        if "ProductVersion" in line:
            value = line.replace('\t', '').split(":")[1]
            version = value.lower()

    return distro, version


class Environment:
    class DebianEnv:
        distro = "Debian"
        version: str
        package_manager = "apt"
        user: str

        def __init__(self, version: str):
            self.version = version
            self.user = os.getlogin()

        def __repr__(self):
            return f"<DebianEnv {self.distro} {self.version}>"

        def __str__(self):
            return f"{self.distro} {self.version}"

    class UbuntuEnv:
        distro = "Ubuntu"
        version: str
        package_manager = "apt"
        user: str

        def __init__(self, version: str):
            self.version = version
            self.user = os.getlogin()

        def __repr__(self):
            return f"<UbuntuEnv {self.distro} {self.version}>"

        def __str__(self):
            return f"{self.distro} {self.version}"

    class AlpineEnv:
        distro = "Alpine"
        version: str
        package_manager = "apk"
        user: str

        def __init__(self, version: str):
            self.version = version
            self.user = os.getlogin()

        def __repr__(self):
            return f"<AlpineEnv {self.distro} {self.version}>"

        def __str__(self):
            return f"{self.distro} {self.version}"

    class MacosEnv:
        distro = "MacOS"
        version: str
        package_manager = "brew"
        user: str

        def __init__(self, version: str):
            self.version = version
            self.user = os.getlogin()

        def __repr__(self):
            return f"<MacosEnv {self.distro} {self.version}>"

        def __str__(self):
            return f"{self.distro} {self.version}"

    os: t.Optional[t.Union[DebianEnv, UbuntuEnv, AlpineEnv, MacosEnv]] = None

    root_dir: Path = Path.cwd()

    conf_dir: Path = root_dir / "conf"
    conf_file: Path = conf_dir / "gitdeploy.conf.json"
    conf = dict()

    log_dir = root_dir / "logs"

    log_file: Path = log_dir / "gitdeploy.log"

    satellite_ini: Path = conf_dir / "satellite.ini"

    repo_dir: Path = root_dir / "repo"
    repo_venv_bin: Path = repo_dir / "venv" / "bin"
    repo_python: Path = repo_venv_bin / "python"
    repo_pip: Path = repo_venv_bin / "pip"
    repo_dot_git_folder: Path = repo_dir / ".git"
    repo_dot_git_config: Path = repo_dot_git_folder / "config"
    repo_requirements_file: Path = repo_dir / "requirements.txt"

    def __init__(self):
        self._check_env()
        self._first_run()

    def _check_env(self):
        compatible_os = {
            "debian": ["10", "11"],
            "ubuntu": ["18.04", "20.04", "22.04", "22.10", "23.04"],
            "alpine": ["3.14", "3.15", "3.16", "3.17"],
            "macos": ["12.6.3"],
        }

        base_cmd = None if sys.platform == 'darwin' else "cat"
        command_name = "sw_vers" if sys.platform == 'darwin' else "/etc/os-release"
        without_base = True if sys.platform == 'darwin' else False

        with Terminator(base_cmd, log=False) as command:
            distro, version = _process_os_release(
                command(command_name, without_base))

            if distro not in compatible_os:
                raise Exception(
                    f"{distro} is not a compatible operating system. "
                    f"Please use one of the following: {compatible_os.keys()}"
                )

            if version not in compatible_os[distro]:
                os_needed = ""
                for key, value in compatible_os.items():
                    os_needed += f"\n{key.capitalize()}"
                    for v in value:
                        os_needed += f" {v}"
                raise Exception(
                    f"{distro} {version} is not a compatible operating system. "
                    f"\nPlease use one of the following:{os_needed}"
                )

        self.os = getattr(self, f"{distro.capitalize()}Env")(version)

    def _first_run(self):
        self.conf_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        self.repo_dir.mkdir(exist_ok=True)
        self.log_file.touch(exist_ok=True)

        if not self.conf_file.exists():
            with open(self.conf_file, "w") as settings:
                settings.write(
                    json.dumps(
                        Resources.generate_default_conf(),
                        indent=4
                    )
                )
