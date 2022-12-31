import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from git import Repo


class Tools:
    @staticmethod
    def generate_random_token(length: int) -> str:
        import secrets
        return secrets.token_hex(length)

    @staticmethod
    def system_log(location: Path, text: str):
        if text == "" or text is None:
            return
        with open(location, "a") as f:
            f.write(f"{text} | \n".strip())

    @staticmethod
    def write_supervisor_config(config_file: Path, config: str):
        with open(config_file, "w") as f:
            f.write(config)

    @staticmethod
    def check_for_none(value: str) -> Union[str, None]:
        str_values = ["null", "none", "undefined"]

        if isinstance(value, str):
            if value.lower() in str_values:
                return None

        if value is None:
            return None

        return value


@dataclass
class DefaultResources:
    autogit_settings = {
        "GIT": None,
        "COMMAND": None,
        "WH_SECRET": Tools.generate_random_token(64),
        "FIRST_RUN": True,
        "T1": Tools.generate_random_token(24),
        "T2": Tools.generate_random_token(24),
    }

    supervisor_config = """
[program:{app}]
directory={dir}
command=venv/bin/{command}
user=root
autostart={autostart}
autorestart={autorestart}
stdout_logfile={log_dir}/{app}.log
stderr_logfile={log_dir}/{app}.log
    """.strip()


class AutoGitExtension:
    """
    A class to handle the control of the git repo and the
    satellite Flask application from within the main Flask application.
    """

    working_dir: Path
    config_dir: Path
    settings_file: Path
    log_dir: Path

    repo: Repo
    repo_dir: Path
    repo_python_instance: Path
    repo_requirements: Path

    autogit_ini: Path
    satellite_ini: Path

    autogit_log: Path
    satellite_log: Path

    allow_supervisor: bool

    def __init__(self, working_dir: Optional[Path] = None, allow_supervisor: bool = True):
        if working_dir is not None:
            self.working_dir = working_dir
        else:
            self.working_dir = Path("/autogit")

        self.config_dir = self.working_dir / "config"
        self.log_dir = self.working_dir / "logs"

        self.repo_dir = self.working_dir / "repo"
        self.repo_python_instance = self.repo_dir / "venv" / "bin" / "python3"
        self.repo_requirements = self.repo_dir / "requirements.txt"

        self.settings_file = self.config_dir / ".autogit.json"

        self.autogit_ini = self.config_dir / "autogit.ini"
        self.satellite_ini = self.config_dir / "satellite.ini"

        self.autogit_log = self.log_dir / "autogit.log"
        self.satellite_log = self.log_dir / "satellite.log"

        self.allow_supervisor = allow_supervisor

    def _run_command(self, command: str, rd: Path = None, supress_logs: bool = False) -> str:
        if rd is None:
            rd = self.working_dir

        command = command.split(" ")
        out, err = "", ""
        process_out, process_err = None, None
        stdout, stderr = None, None

        try:
            process = subprocess.run(command, capture_output=True, cwd=rd, timeout=120)
            stdout = process.stdout.decode(encoding='UTF-8')
            stderr = process.stderr.decode(encoding='UTF-8')
        except Exception as e:
            process_err = e

        if stdout:
            process_out = stdout

        if stderr:
            process_err = stderr

        if process_out:
            out = f" :OUT: {process_out} \n"
        if process_err:
            err = f" :ERR: {process_err} \n"

        if not supress_logs:
            Tools.system_log(self.autogit_log, f"{out} {err}")
        return out + err

    def _write_satellite_ini(self, command: str):
        Tools.write_supervisor_config(
            self.satellite_ini,
            DefaultResources.supervisor_config.format(
                app="satellite",
                dir=self.repo_dir,
                command=command,
                autostart="true",
                autorestart="false",
                log_dir=self.log_dir,
            )
        )

    def setup(self):
        """

        Creates the following directories used by the extension:
        - cwd/config
        - cwd/logs
        - cwd/repo
        - /etc/supervisor.d

        Creates the following files used by the extension:
        - cwd/config/.autogit.json
        - cwd/config/satellite.ini

        :return:
        """
        directories = [
            self.config_dir,
            self.log_dir,
            self.repo_dir,
        ]
        # Create directories
        for directory in directories:
            directory.mkdir(exist_ok=True)

        files = [
            self.autogit_log,
            self.satellite_log,
        ]
        # Create directories
        for file in files:
            file.touch(exist_ok=True)

        if not self.settings_file.exists():
            self.write_settings(
                DefaultResources.autogit_settings,
                auto_actions=False
            )

        if not self.satellite_ini.exists():
            self._write_satellite_ini("python3 --version")

    def auto_deploy(self):
        if self.settings_file.exists():
            settings = self.read_settings()
            git = settings.get("GIT")
            command = settings.get("COMMAND")
            if git is not None and command is not None:
                self.repo_clone(git)
                self.repo_create_venv()
                self.repo_install_requirements()
                self._write_satellite_ini(command)
                if self.allow_supervisor:
                    self.supervisorctl_reread()
                    self.supervisorctl_update()
                    self.restart_satellite()

    def read_settings(self) -> dict:
        with open(self.settings_file, "r") as f:
            return json.load(f)

    def write_settings(self, new_settings: dict, auto_actions: bool = True) -> None:
        clean_settings = dict()

        for key, value in new_settings.items():
            clean_settings[key] = Tools.check_for_none(value)

        if self.settings_file.exists():
            old_settings = self.read_settings()
            if auto_actions:
                if clean_settings.get("GIT") != old_settings.get("GIT"):
                    self.repo_destroy()
                    self.repo_clone(clean_settings.get("GIT"))
                    self.repo_create_venv()
                    self.repo_install_requirements()

            if clean_settings.get("COMMAND") != old_settings.get("COMMAND"):
                self._write_satellite_ini(clean_settings.get("COMMAND"))
                if auto_actions:
                    self.supervisorctl_reread()
                    self.supervisorctl_update()
                    self.restart_satellite()

        with open(self.settings_file, "w") as f:
            json.dump(clean_settings, f, indent=4)

    def set_tokens(self, current_settings) -> dict:
        if self.settings_file.exists():
            settings = current_settings
            settings["T1"] = Tools.generate_random_token(24)
            settings["T2"] = Tools.generate_random_token(24)
            self.write_settings(settings)
            return settings

    def read_autogit_log(self) -> list:
        if self.autogit_log.exists():
            with open(self.autogit_log, "r") as f:
                logs = f.readlines()
            if logs:
                return logs
        return ["No logs found"]

    def del_autogit_log(self):
        self.autogit_log.unlink(missing_ok=True)
        self.autogit_log.touch(exist_ok=True)

    def read_satellite_log(self) -> list:
        if self.satellite_log.exists():
            with open(self.satellite_log, "r") as f:
                logs = f.readlines()
            if logs:
                return logs
        return ["No logs found"]

    def del_satellite_log(self):
        self.satellite_log.unlink(missing_ok=True)
        self.satellite_log.touch(exist_ok=True)

    def repo_clone(self, repo_url: str) -> bool:
        if not Path(self.repo_dir / ".git").exists():
            try:
                self.repo = Repo.clone_from(repo_url, self.repo_dir)
                Tools.system_log(self.autogit_log, f"REPO ::: Repo cloned from {repo_url}")
                return True
            except Exception as e:
                Tools.system_log(self.autogit_log, f"ERROR ::: Cloning repo: {e}")
                return False

        Tools.system_log(self.autogit_log, f"INFO ::: Repo already exists")
        return False

    def repo_pull(self) -> bool:
        if Path(self.repo_dir / ".git").exists():
            try:
                Repo(self.repo_dir).remotes.origin.pull()
                return True
            except Exception as e:
                Tools.system_log(self.autogit_log, f"ERROR ::: Pulling repo: {e}")

        Tools.system_log(self.autogit_log, f"INFO ::: No repo exists at {self.repo_dir}")
        return False

    def repo_create_venv(self):
        if self.repo_dir.exists():
            if Path(self.repo_dir / "venv").exists():
                self._run_command(f"rm -rf venv", rd=self.repo_dir)
            try:
                self._run_command("python3 -m venv venv", rd=self.repo_dir)
                Tools.system_log(self.autogit_log, f"REPO ::: Repo venv created")
            except Exception as e:
                raise RuntimeError(f"ERROR ::: creating venv: {e}")
        else:
            raise FileNotFoundError("ERROR ::: Repo directory not found")

    def repo_install_requirements(self):
        if self.repo_python_instance.exists() and self.repo_requirements.exists():
            try:
                self._run_command(f"{self.repo_python_instance} -m pip install -r {self.repo_requirements}", rd=self.repo_dir)
            except Exception as e:
                raise RuntimeError(f"ERROR ::: installing requirements: {e}")

        else:
            raise FileNotFoundError("ERROR ::: Python instance or requirements.txt not found")

    def repo_destroy(self):
        if self.repo_dir.exists():
            self._run_command("rm -rf repo")
            self.repo_dir.mkdir(exist_ok=True)
        else:
            raise FileNotFoundError("ERROR ::: Repo directory not found")

    def repo_first_run(self) -> bool:
        ac = self.read_settings()
        if ac.get("GIT", None):

            try:
                self.repo_clone(ac["GIT"])
            except Exception as e:
                Tools.system_log(self.autogit_log, f"ERROR ::: ::: cloning repo: {e}")
                return False

            try:
                self.repo_create_venv()
            except Exception as e:
                Tools.system_log(self.autogit_log, f"ERROR ::: creating venv: {e}")
                return False

            try:
                self.repo_install_requirements()
            except Exception as e:
                Tools.system_log(self.autogit_log, f"ERROR ::: Unable to install requirements: {e}")
                return False

            Tools.system_log(self.autogit_log, f"OK ::: Repo cloned, venv created and requirements installed")
            return True

        return False

    def start_supervisor(self):
        if self.allow_supervisor:
            try:
                self._run_command("/usr/bin/supervisord")
            except Exception as e:
                Tools.system_log(self.autogit_log, f"ERROR ::: Unable to start supervisord {e}")

    def supervisorctl(self, action, app):
        if self.allow_supervisor:
            try:
                return self._run_command(f"supervisorctl {action} {app}")
            except Exception as e:
                error = f"ERROR ::: supervisorctl {action} {app}: {e}"
                Tools.system_log(self.autogit_log, error)
                return error
        return "ERROR ::: Supervisor disabled"

    def supervisorctl_status(self, app, supress_logs: bool = False) -> str:
        if self.allow_supervisor:
            try:
                return self._run_command(f"supervisorctl status {app}", supress_logs=True)
            except Exception as e:
                error = f"ERROR ::: supervisorctl status {app}: {e}"
                if not supress_logs:
                    Tools.system_log(self.autogit_log, error)
                return error

    def supervisorctl_reread(self):
        if self.allow_supervisor:
            try:
                self._run_command(f"supervisorctl reread")
            except Exception as e:
                Tools.system_log(self.autogit_log, f"ERROR ::: supervisorctl reread: {e}")

    def supervisorctl_update(self):
        if self.allow_supervisor:
            try:
                self._run_command(f"supervisorctl update")
            except Exception as e:
                Tools.system_log(self.autogit_log, f"ERROR ::: supervisorctl update: {e}")

    def status_satellite(self) -> bool:
        if self.allow_supervisor:
            _ = self.supervisorctl_status("satellite", supress_logs=True)

            if isinstance(_, str):
                if "STOPPED" in _:
                    return False
                elif "RUNNING" in _:
                    return True
                if "started" in _:
                    return True

            return False

    def start_satellite(self) -> str:
        self.supervisorctl_reread()
        self.supervisorctl_update()
        return self.supervisorctl("start", "satellite")

    def stop_satellite(self):
        self.supervisorctl("stop", "satellite")

    def restart_satellite(self):
        self.supervisorctl("restart", "satellite")

    def start_autogit(self):
        self.supervisorctl("start", "autogit")

    def stop_autogit(self):
        self.supervisorctl("stop", "autogit")

    def restart_autogit(self):
        self.supervisorctl("restart", "autogit")
