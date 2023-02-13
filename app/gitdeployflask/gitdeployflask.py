import json
import typing as t
from pathlib import Path

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

    return distro, version


class GitDeployFlask:
    class DebianEnv:
        distro = "Debian"
        version: str
        package_manager = "apt"

        def __init__(self, version: str):
            self.version = version

        def __repr__(self):
            return f"<DebianEnv {self.distro} {self.version}>"

        def __str__(self):
            return f"{self.distro} {self.version}"

    class UbuntuEnv:
        distro = "Ubuntu"
        version: str
        package_manager = "apt"

        def __init__(self, version: str):
            self.version = version

        def __repr__(self):
            return f"<UbuntuEnv {self.distro} {self.version}>"

        def __str__(self):
            return f"{self.distro} {self.version}"

    class AlpineEnv:

        distro = "Alpine"
        version: str
        package_manager = "apk"

        def __init__(self, version: str):
            self.version = version

        def __repr__(self):
            return f"<AlpineEnv {self.distro} {self.version}>"

        def __str__(self):
            return f"{self.distro} {self.version}"

    env: t.Optional[t.Union[DebianEnv, UbuntuEnv, AlpineEnv]] = None
    root_dir: Path = Path.cwd()

    conf_dir: Path = root_dir / "conf"
    conf_file: Path = conf_dir / "gitdeploy.conf.json"
    conf = dict()

    log_dir = root_dir / "logs"

    supervisor_process: None
    supervisor_dir: Path = root_dir / "supervisor"
    supervisor_conf: Path = supervisor_dir / "supervisord.conf"
    supervisor_log: Path = log_dir / "supervisord.log"

    satellite_ini: Path = root_dir / "satellite.ini"
    satellite_log: Path = log_dir / "satellite.log"

    repo_dir: Path = root_dir / "repo"
    repo_venv_bin: Path = repo_dir / "venv" / "bin"
    repo_python: Path = repo_venv_bin / "python"
    repo_pip: Path = repo_venv_bin / "pip"
    repo_git_file: Path = repo_dir / ".git"
    repo_git_config: Path = repo_git_file / "config"
    repo_requirements_file: Path = repo_dir / "requirements.txt"

    dummy_command = "echo 'Waiting for command to be set...'"

    def __init__(self):
        self._check_env()
        self._first_run()

    def _check_env(self):
        compatible_os = {
            "debian": ["10", "11"],
            "ubuntu": ["18.04", "20.04", "22.04", "22.10", "23.04"],
            "alpine": ["3.14", "3.15", "3.16", "3.17"]
        }
        with Terminator("cat") as command:
            stout, sterr = command("/etc/os-release")
            if sterr:
                raise Exception(
                    f"Error while checking operating system: {sterr}"
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
        self.satellite_log.touch(exist_ok=True)

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
                        supervisor_dir=self.supervisor_dir,
                        log_dir=self.log_dir,
                        conf_dir=self.conf_dir,
                    )
                )

        self.read_conf()

        if not self.satellite_ini.exists():
            with open(self.satellite_ini, "w") as ini:
                ini.write(
                    Resources.generate_satellite_ini(
                        app="satellite",
                        command=self.conf.get("COMMAND", self.dummy_command),
                        autostart=True,
                        autorestart=False,
                        log_location=self.satellite_log,
                        working_directory=self.repo_dir
                    )
                )

    def set_conf(self, key: str, value: t.Any, write: bool = False):
        if key not in self.conf:
            raise KeyError(f"Key '{key}' not found in conf file")

        self.conf[key] = value

        if write:
            self.write_conf()

    def read_conf(self):
        with open(self.conf_file, "r") as conf:
            self.conf = json.load(conf)

    def write_conf(self):
        with open(self.conf_file, "w") as conf:
            json.dump(self.conf, conf, indent=4)

    def set_tokens(self):
        self.set_conf("T1", Tools.generate_random_token(24))
        self.set_conf("T2", Tools.generate_random_token(24))
        self.set_conf("FIRST_RUN", Tools.generate_random_token(24))
        self.write_conf()

    def clone_repo(self):
        with Terminator("git") as git:
            o1, e1 = git("clone", self.conf.get("GIT"), self.repo_dir)
            o2, e2 = git("checkout", self.conf.get("GIT_BRANCH", "master"), working_directory=self.repo_dir)
            if e1 or e2:
                return False
            return True

    def create_venv(self):
        with Terminator("python3") as python:
            o1, e1 = python("-m", "venv", self.repo_venv_bin.parent)
            if e1:
                return False
            return True

    def install_requirements(self):
        with Terminator("pip", working_directory=self.repo_venv_bin) as pip:
            o1, e1 = pip("install", "-r", self.repo_requirements_file)
            if e1:
                return False
            return True

    def update_repo(self):
        with Terminator("git") as git:
            o1, e1 = git("pull", working_directory=self.repo_dir)
            if e1:
                return False
            return True

    def destroy_repo(self):
        with Terminator("rm") as rm:
            o1, e1 = rm(f"-rf {self.repo_dir}")
            self.repo_dir.mkdir(exist_ok=True)
            if e1:
                return False
            return True

    def destroy_venv(self):
        with Terminator("rm") as rm:
            o1, e1 = rm(f"-rf {self.repo_venv_bin.parent}")
            self.repo_venv_bin.parent.mkdir(exist_ok=True)
            if e1:
                return False
            return True

    @staticmethod
    def status_satellite():
        with Terminator("supervisorctl") as ctl:
            o1, e1 = ctl("status satellite")
            if e1:
                return False
            return True

    @staticmethod
    def start_satellite():
        with Terminator("supervisorctl") as ctl:
            o1, e1 = ctl("start satellite")
            if e1:
                return False
            return True

    @staticmethod
    def stop_satellite():
        with Terminator("supervisorctl") as ctl:
            o1, e1 = ctl("satellite start")
            if e1:
                return False
            return True

    @staticmethod
    def restart_satellite():
        with Terminator("supervisorctl") as ctl:
            o1, e1 = ctl("restart satellite")
            if e1:
                return False
            return True

    def get_satellite_logs(self):
        with open(self.satellite_log, "r") as log:
            return log.read()
