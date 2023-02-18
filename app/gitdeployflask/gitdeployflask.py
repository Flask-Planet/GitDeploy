import json
import os
import re
import sys
import typing as t
from pathlib import Path

from .resources import Resources
from .terminator import Terminator
from .tools import Tools


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


def _failed(outputs: t.List[str], fail_on: t.List[str] = None):
    complete = ""
    for output in outputs:
        complete += output

    for fail in fail_on:
        if fail in complete:
            return True
    return False


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

    env: t.Optional[t.Union[DebianEnv, UbuntuEnv, AlpineEnv, MacosEnv]] = None
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
    repo_dot_git_folder: Path = repo_dir / ".git"
    repo_dot_git_config: Path = repo_dot_git_folder / "config"
    repo_requirements_file: Path = repo_dir / "requirements.txt"

    dummy_command = "echo 'Waiting for command to be set...'"

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

    def get_repo_contents(self) -> t.List[str]:
        return os.listdir(self.repo_dir)

    def supervisor_update(self):
        with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
            ctl("update")

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

    def _write_dot_git_config(self, new_url):
        if self.repo_dot_git_config.exists():
            with open(self.repo_dot_git_config, "r") as old_config:
                old_config_ = old_config.read()
                with open(self.repo_dot_git_config, "w") as new_config:
                    new_config_ = re.sub(r"(?<=url = ).*", new_url, old_config_)
                    new_config.write(new_config_)

    def set_dot_git_config_with_token(self) -> bool:
        git_url = self.conf.get("GIT_URL")
        token_name = self.conf.get("GIT_TOKEN_NAME")
        token = self.conf.get("GIT_TOKEN")

        new_git = git_url.replace("https://", f"https://{token_name}:{token}@")
        self.set_conf("GIT", new_git, write=True)
        self._write_dot_git_config(new_git)
        return True

    def set_dot_git_config_without_token(self) -> bool:
        git_url = self.conf.get("GIT_URL")
        self.set_conf("GIT", git_url, write=True)
        self._write_dot_git_config(git_url)
        return True

    def write_satellite_ini(self):
        with open(self.satellite_ini, "w") as ini:
            ini.write(
                Resources.generate_satellite_ini(
                    app="satellite",
                    command=self._parse_command(),
                    user=self.env.user,
                    autostart=False,
                    autorestart=False,
                    log_location=self.log_file,
                    working_directory=self.repo_dir
                )
            )
        self.supervisor_update()

    def set_tokens(self):
        self.set_conf("T1", Tools.generate_random_token(24))
        self.set_conf("T2", Tools.generate_random_token(24))
        self.set_conf("FIRST_RUN", False)
        self.write_conf()

    def clone_repo(self):
        with Terminator("git", type_="pexpect") as git:
            return git(
                f"clone {self.conf.get('GIT')} {self.repo_dir}",
                expects={"Username": None}
            )

    def create_venv(self):
        with Terminator("python3") as python:
            python(f"-m venv {self.repo_venv_bin.parent}")

    def install_requirements(self):
        if self.repo_pip.exists():
            with Terminator("venv/bin/pip", working_directory=self.repo_dir) as pip:
                pip(f"install -r {self.repo_requirements_file}")

    def update_repo(self):
        with Terminator("git") as git:
            return git("pull", working_directory=self.repo_dir)

    def destroy_repo(self):
        with Terminator("rm") as rm:
            rm(f"-rf {self.repo_dir}")
            self.repo_dir.mkdir(exist_ok=True)

    def destroy_venv(self):
        with Terminator("rm") as rm:
            rm(f"-rf {self.repo_venv_bin.parent}")

    def status_satellite(self):
        with Terminator(
                "venv/bin/supervisorctl -c supervisor/supervisord.conf",
                type_="pexpect_supervisor",
                log=False
        ) as ctl:
            output = ctl("status satellite")

        for line in output:
            if "FATAL" in line:
                return False
        return True

    def start_satellite(self):
        if self.conf.get("COMMAND") is not None:
            with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
                ctl("start satellite")

    def stop_satellite(self):
        if self.conf.get("COMMAND") is not None:
            with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
                ctl("stop satellite")

    def restart_satellite(self):
        if self.conf.get("COMMAND") is not None:
            with Terminator("venv/bin/supervisorctl -c supervisor/supervisord.conf") as ctl:
                ctl("restart satellite")

    def read_logs(self) -> list:
        logs = self.log_file.read_text().split("\n")
        return [x for x in logs if x]

    def clear_logs(self):
        self.log_file.unlink()
        self.log_file.touch()
