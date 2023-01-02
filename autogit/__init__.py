import json
from pathlib import Path

from .logger import Logger
from .pip_cli import PipCli
from .git_cli import GitCli
from .resources import Resources
from .supervisor import SupervisorctlController, SupervisorIni, Supervisor
from .terminal import Terminal
from .tools import Tools


class AutoGit:
    """
    A class to handle the control of the git repo and the
    satellite Flask application from within the main Flask application.
    """

    working_dir: Path
    config_dir: Path
    log_dir: Path

    settings_file: Path

    repo_dir: Path
    repo_python_instance: Path
    repo_venv_bin: Path
    repo_requirements: Path

    supervisor: Supervisor

    satellite_ini: SupervisorIni

    log_file_path: Path

    allow_supervisor: bool

    def __init__(self, allow_supervisor: bool = True):

        # Set supervisor control flag
        self.allow_supervisor = allow_supervisor

        # directories
        self.working_dir = Path.cwd()
        self.config_dir = self.working_dir / "config"
        self.log_dir = self.working_dir / "logs"
        self.repo_dir = self.working_dir / "repo"

        self.settings_file = self.config_dir / ".autogit.json"
        self.log_file_path = self.log_dir / "autogit.log"

        self.repo_venv_bin = self.repo_dir / "venv" / "bin"
        self.repo_python_instance = self.repo_venv_bin / "python3"
        self.repo_requirements = self.repo_dir / "requirements.txt"
        self.repo_git_config = self.repo_dir / ".git" / "config"

        # set logger
        self.logger = Logger(self.log_file_path)

        self.supervisor = Supervisor(
            "/etc/supervisord.conf",
            f"{self.config_dir}",
        )

        self.satellite_ini = SupervisorIni(
            path=self.config_dir / "satellite.ini",
            app="satellite",
            working_directory=f"{self.repo_dir}",
            command=f"echo 'Command not set'",
            autostart=False,
            autorestart=False,
            log_location=f"{self.log_file_path}"
        )

    def setup(self):
        """
        Creates the following files used by the extension:
        - cwd/config/.autogit.json
        - cwd/config/satellite.ini

        :return:
        """

        self.repo_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        self.log_file_path.touch(exist_ok=True)

        if not self.satellite_ini.path.exists():
            self.supervisor.write_init(self.satellite_ini)

        if not self.settings_file.exists():
            self.write_settings(Resources.autogit_settings)

    def auto_deploy(self):
        if self.settings_file.exists():
            settings = self.read_settings()
            git = settings.get("GIT")
            command = settings.get("COMMAND")
            if git is not None:
                self.repo_clone(git)
                self.repo_create_venv()
                if self.repo_requirements.exists() and self.repo_python_instance.exists():
                    self.repo_install_requirements()
                else:
                    self.logger.log("ERROR ::: Auto deploy stopped. No requirements.txt file found in repo")
                    return

            if command is not None:
                self.satellite_ini.command = command
                self.supervisor.write_init(self.satellite_ini)

                if self.allow_supervisor:
                    with SupervisorctlController(['reread', 'update', 'restart satellite']) as output:
                        self.logger.log(output)

    def read_settings(self) -> dict:
        with open(self.settings_file, "r") as f:
            return json.load(f)

    def write_settings(self, new_settings: dict) -> None:
        clean_settings = dict()

        for key, value in new_settings.items():
            clean_settings[key] = Tools.check_for_none(value)

        if self.settings_file.exists():
            old_settings = self.read_settings()

            private = clean_settings.get("GIT_PRIVATE", None)
            url = clean_settings.get("GIT_URL", None)

            if private:

                git_url = clean_settings.get("GIT_URL")
                git_username = clean_settings.get("GIT_USERNAME")
                git_password = clean_settings.get("GIT_PASSWORD")

                proto_call = git_url.split("://")[0]

                if proto_call == "https":
                    clean_settings["GIT"] = git_url.replace("https://", f"https://{git_username}:{git_password}@")
                else:
                    clean_settings["GIT"] = git_url.replace("http://", f"http://{git_username}:{git_password}@")

            else:

                clean_settings["GIT"] = url
                clean_settings["GIT_USERNAME"] = None
                clean_settings["GIT_PASSWORD"] = None

            if self.repo_git_config.exists():
                with open(self.repo_git_config, "r") as f:
                    git_config = f.read()

                git_config = git_config.replace(f"url = {old_settings.get('GIT')}", f"url = {clean_settings.get('GIT')}")

                with open(self.repo_git_config, "w") as f:
                    f.write(git_config)

            if clean_settings.get("COMMAND") != old_settings.get("COMMAND"):
                if clean_settings.get("COMMAND") is not None:
                    self.satellite_ini.command = f"{Path(self.repo_venv_bin / clean_settings.get('COMMAND'))}"
                    self.supervisor.write_init(self.satellite_ini)

                with SupervisorctlController(['reread', 'update', 'restart satellite']) as output:
                    self.logger.log(output)

        with open(self.settings_file, "w") as f:
            json.dump(clean_settings, f, indent=4)

    def set_tokens(self, current_settings) -> dict:
        if self.settings_file.exists():
            settings = current_settings
            settings["T1"] = Tools.generate_random_token(24)
            settings["T2"] = Tools.generate_random_token(24)
            settings["FIRST_RUN"] = False
            self.write_settings(settings)
            return settings

    def read_autogit_log(self) -> list:
        if self.log_file_path.exists():
            with open(self.log_file_path, "r") as f:
                logs = f.readlines()
            if logs:
                return logs
        return ["No logs found"]

    def del_autogit_log(self):
        self.log_file_path.unlink(missing_ok=True)
        self.log_file_path.touch(exist_ok=True)

    def repo_clone(self, repo_url: str) -> bool:
        if not Path(self.repo_dir / ".git").exists():
            try:
                with GitCli(f"clone {repo_url} .", self.repo_dir) as output:
                    self.logger.log(output)
                self.logger.log(f"INFO ::: Repo cloned")
                return True
            except Exception as e:
                self.logger.log(f"ERROR ::: Cloning repo: {e}")
                return False

        self.logger.log(f"INFO ::: Repo already exists")
        return False

    def repo_pull(self) -> bool:
        if Path(self.repo_dir / ".git").exists():
            try:
                with GitCli(f"pull", self.repo_dir) as output:
                    self.logger.log(output)
                self.logger.log(f"INFO ::: Repo pulled")
                return True
            except Exception as e:
                self.logger.log(f"ERROR ::: Pulling repo: {e}")

        self.logger.log(f"INFO ::: Unable to pull repo {self.repo_dir}")
        return False

    def repo_create_venv(self):
        if self.repo_dir.exists():
            if Path(self.repo_dir / "venv").exists():
                self.logger.log(f"ERROR ::: venv already exists")
                return False
            else:
                with Terminal("python3 -m venv venv", cwd=self.repo_dir) as output:
                    self.logger.log(f"INFO ::: venv created {output}")
                    return True
        self.logger.log(f"ERROR ::: repo dir does not exist")
        return False

    def repo_destroy_venv(self):
        if self.repo_dir.exists():
            with Terminal(f"rm -rf venv", cwd=self.repo_dir):
                self.logger.log(f"INFO ::: venv destroyed")

    def repo_install_requirements(self):
        if self.repo_python_instance.exists():
            with PipCli(f"install -r requirements.txt", cwd=self.repo_dir) as output:
                self.logger.log(output)
                return True
        self.logger.log(f"ERROR ::: repo python instance does not exist, install venv first")
        return False

    def repo_destroy(self):
        if self.repo_dir.exists():
            with Terminal(f"rm -rf repo", cwd=self.working_dir):
                self.logger.log(f"INFO ::: repo destroyed")
            self.repo_dir.mkdir(exist_ok=True)
        else:
            self.repo_dir.mkdir(exist_ok=True)

    def supervisorctl_status(self, app, supress_logs: bool = False) -> str:
        if self.allow_supervisor:
            with SupervisorctlController([f'status {app}']) as output:
                if not supress_logs:
                    self.logger.log(output)
                if len(output) > 1:
                    return str(output[-1])
                return str(output[0])

    def supervisorctl_reread(self):
        if self.allow_supervisor:
            with SupervisorctlController(['reread']) as output:
                self.logger.log(output)

    def supervisorctl_update(self):
        if self.allow_supervisor:
            with SupervisorctlController(['update']) as output:
                self.logger.log(output)

    def start_satellite(self) -> str:
        if self.allow_supervisor:
            with SupervisorctlController(['reread', 'update', 'start satellite']) as output:
                self.logger.log(output)
        return " ".join(output)

    def stop_satellite(self):
        with SupervisorctlController(['stop satellite']) as output:
            self.logger.log(output)

    def restart_satellite(self):
        with SupervisorctlController(['reread', 'update', 'restart satellite']) as output:
            self.logger.log(output)
