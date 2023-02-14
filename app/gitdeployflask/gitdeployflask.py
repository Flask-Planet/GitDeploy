import json
import os
import sys
import typing as t
from pathlib import Path

from .logger import Logger
from .resources import Resources
from .terminator import Terminator
from .tools import Tools


def _process_os_release(stout):
    split_output = stout.split("\n")
    distro = None
    version = None
    for line in split_output:
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


class GitDeployFlask:
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

    env: t.Optional[t.Union[DebianEnv, UbuntuEnv, AlpineEnv]] = None
    root_dir: Path = Path.cwd()

    conf_dir: Path = root_dir / "conf"
    conf_file: Path = conf_dir / "gitdeploy.conf.json"
    conf = dict()

    log_dir = root_dir / "logs"

    log_file: Path = log_dir / "gitdeploy.log"

    supervisor_process: None
    supervisor_dir: Path = root_dir / "supervisor"
    supervisor_conf: Path = supervisor_dir / "supervisord.conf"
    supervisor_log: Path = log_dir / "supervisord.log"

    satellite_ini: Path = conf_dir / "satellite.ini"

    repo_dir: Path = root_dir / "repo"
    repo_venv_bin: Path = repo_dir / "venv" / "bin"
    repo_python: Path = repo_venv_bin / "python"
    repo_pip: Path = repo_venv_bin / "pip"
    repo_git_file: Path = repo_dir / ".git"
    repo_git_config: Path = repo_git_file / "config"
    repo_requirements_file: Path = repo_dir / "requirements.txt"

    dummy_command = "echo 'Waiting for command to be set...'"

    logger = Logger()

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

        with Terminator(base_cmd) as command:
            stout, sterr = command(command_name, without_base)
            if sterr:
                raise Exception(
                    f"Info on checking operating system: {sterr}"
                )

            distro, version = _process_os_release(stout)

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

        self.env = getattr(self, f"{distro.capitalize()}Env")(version)

    def _first_run(self):
        self.conf_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        self.supervisor_dir.mkdir(exist_ok=True)
        self.repo_dir.mkdir(exist_ok=True)

        self.supervisor_log.touch(exist_ok=True)
        self.log_file.touch(exist_ok=True)

        if not self.conf_file.exists():
            with open(self.conf_file, "w") as settings:
                settings.write(
                    json.dumps(
                        Resources.generate_default_conf(),
                        indent=4
                    )
                )

        if not self.supervisor_conf.exists():
            with open(self.supervisor_conf, "w") as conf:
                conf.write(
                    Resources.generate_supervisor_conf(
                        supervisor_dir=self._remove_cwd(self.supervisor_dir),
                        log_dir=self._remove_cwd(self.log_dir),
                        conf_dir=str(self.conf_dir),
                    )
                )

        self.read_conf()
        self.logger.init_log_file(self.log_file)

        if not self.satellite_ini.exists():
            self.write_satellite_ini()
        else:
            self.start_satellite()

    def _parse_command(self) -> str:
        command = "echo 'Waiting for command to be set...'"
        if self.repo_venv_bin.exists():
            os.listdir(self.repo_venv_bin)
            if self.conf.get("COMMAND"):
                start_command = self.conf.get("COMMAND").split(" ")[0]
                if start_command in os.listdir(self.repo_venv_bin):
                    command = f"venv/bin/{self.conf.get('COMMAND')}"
        return command

    def _remove_cwd(self, path: Path) -> str:
        return str(path).replace(str(self.root_dir), "").lstrip("/")

    def supervisor_update(self):
        with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
            o1, e1 = ctl("update")
            self.logger.log(f"Supervisor updated")
            if e1:
                self.logger.log(f"Info on updating supervisor: {e1}")

            o1, e1 = ctl("restart all")
            self.logger.log(f"Supervisor restarted")
            if e1:
                self.logger.log(f"Info on restarting supervisor: {e1}")

    def set_conf(self, key: str, value: t.Any, write: bool = False):
        if key not in self.conf:
            raise KeyError(f"Key '{key}' not found in conf file")

        self.conf[key] = value

        if write:
            self.write_conf()

    def read_conf(self):
        with open(self.conf_file, "r") as conf:
            self.conf = json.load(conf)

    def write_conf(self, new_conf: t.Optional[dict] = None):
        with open(self.conf_file, "w") as conf:
            if new_conf:
                json.dump(new_conf, conf, indent=4)
            else:
                json.dump(self.conf, conf, indent=4)

    def write_satellite_ini(self):
        with open(self.satellite_ini, "w") as ini:
            ini.write(
                Resources.generate_satellite_ini(
                    app="satellite",
                    command=self._parse_command(),
                    user=self.env.user,
                    autostart=True,
                    autorestart=False,
                    log_location=self.log_file,
                    working_directory=self.repo_dir
                )
            )
        self.supervisor_update()

    def set_tokens(self):
        self.set_conf("T1", Tools.generate_random_token(24))
        self.set_conf("T2", Tools.generate_random_token(24))
        self.set_conf("FIRST_RUN", Tools.generate_random_token(24))
        self.write_conf()

    def clone_repo(self):
        with Terminator("git") as git:
            o1, e1 = git(f"clone {self.conf.get('GIT_URL')} {self.repo_dir}")
            o2, e2 = git(f"checkout {self.conf.get('GIT_BRANCH', 'master')}", working_directory=self.repo_dir)
            self.logger.log(f"Cloning repo: {o1}{o2}")
            if e1 or e2:
                self.logger.log(f"Info on cloning repo: {e1}{e2}")
                return False
            return True

    def create_venv(self):
        with Terminator("python3") as python:
            o1, e1 = python(f"-m venv {self.repo_venv_bin.parent}")
            self.logger.log(f"Creating venv: {o1}")
            if e1:
                self.logger.log(f"Info on creating venv: {e1}")
                return False
            return True

    def install_requirements(self):
        with Terminator("venv/bin/pip", working_directory=self.repo_dir) as pip:
            o1, e1 = pip(f"install -r {self.repo_requirements_file}")
            self.logger.log(f"Installing requirements: {o1}")
            if e1:
                self.logger.log(f"Info on installing requirements: {e1}")
                return False
            return True

    def update_repo(self):
        with Terminator("git") as git:
            o1, e1 = git("pull", working_directory=self.repo_dir)
            self.logger.log(f"Updating repo: {o1}")
            if e1:
                self.logger.log(f"Info on updating repo: {e1}")
                return False
            return True

    def destroy_repo(self):
        with Terminator("rm") as rm:
            o1, e1 = rm(f"-rf {self.repo_dir}")
            self.repo_dir.mkdir(exist_ok=True)
            self.logger.log(f"Destroying repo: {o1}")
            if e1:
                self.logger.log(f"Info on destroying repo: {e1}")
                return False
            return True

    def destroy_venv(self):
        with Terminator("rm") as rm:
            o1, e1 = rm(f"-rf {self.repo_venv_bin.parent}")
            self.logger.log(f"Destroying venv: {o1}")
            if e1:
                self.logger.log(f"Info on destroying venv: {e1}")
                return False
            return True

    def status_satellite(self):
        with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
            o1, e1 = ctl("status satellite")
            self.logger.log(f"Satellite status: {o1}")
            if e1:
                self.logger.log(f"Info on getting satellite status: {e1}")
                return False
            return True

    def start_satellite(self):
        with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
            o1, e1 = ctl("start satellite")
            self.logger.log(f"Satellite start: {o1}")
            if e1:
                self.logger.log(f"Info on starting satellite: {e1}")
                return False
            return True

    def stop_satellite(self):
        with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
            o1, e1 = ctl("satellite start")
            self.logger.log(f"Satellite stop: {o1}")
            if e1:
                self.logger.log(f"Info on stopping satellite: {e1}")
                return False
            return True

    def restart_satellite(self):
        with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
            o1, e1 = ctl("restart satellite")
            self.logger.log(f"Satellite restart: {o1}")
            if e1:
                self.logger.log(f"Info on restarting satellite: {e1}")
                return False
            return True

    def read_logs(self) -> list:
        logs = self.log_file.read_text().split("\n")
        return [x for x in logs if x]

    def clear_logs(self):
        self.logger.clear_log()
