import json
import os
import pathlib
import secrets
import shutil
import signal
import string
import subprocess as sp
from typing import Optional

from git import Repo

current_location = pathlib.Path(__file__).parent.absolute()
os.chdir(current_location)
settings_file = pathlib.Path(pathlib.Path.cwd() / ".autogit.json")
repo_folder = pathlib.Path(pathlib.Path.cwd() / "repo")


def wash_command(command) -> list:
    nc = command.split(" ")
    nc[0] = f'{pathlib.Path(repo_folder / "venv" / "bin" / nc[0])}'
    return nc


def generate_random_token(length: int) -> str:
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


default_settings = {
    "GIT": None,
    "COMMAND": None,
    "WH_SECRET": generate_random_token(128),
    "T1": None,
    "T2": None,
    "T3": None,
}


def init_settings():
    if not settings_file.exists():
        write_settings(default_settings)


def read_settings() -> dict:
    if not settings_file.exists():
        write_settings(default_settings)
    with open(settings_file) as f:
        return json.load(f)


def write_settings(json_dict: dict):
    with open(settings_file, "w") as f:
        f.write(json.dumps(json_dict, indent=4))


class SatelliteAppController:
    process: Optional[sp.Popen]

    def __init__(self):
        self.process = None

    def status(self):
        if hasattr(self.process, 'pid'):
            return True
        return False

    def start(self, COMMAND: list):
        if hasattr(self.process, 'pid'):
            return False
        try:
            self.process = sp.Popen(
                COMMAND,
                cwd=pathlib.Path(pathlib.Path.cwd() / "repo"),
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                start_new_session=True,
            )
        except FileNotFoundError:
            return False
        return True

    def stop(self):
        try:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            while True:
                if self.process.poll() is not None:
                    break
            self.process = None
            return True
        except (ProcessLookupError, AttributeError):
            return False


class AppController:
    satellite_app: SatelliteAppController

    def __init__(self, create_flask_app):
        self.create_flask_app = create_flask_app
        self.satellite_app = SatelliteAppController()

    def __enter__(self):
        return self.create_flask_app(self.satellite_app)

    def __exit__(self, type_, value, traceback):
        self.satellite_app.stop()


class Gitter:
    git_repo_url: str
    repo: Repo

    REPO_FOLDER = pathlib.Path(pathlib.Path.cwd() / "repo")
    PYTHON_INSTANCE = pathlib.Path(REPO_FOLDER / "venv" / "bin" / "python3")
    REQ = pathlib.Path(REPO_FOLDER / "requirements.txt")

    def __init__(self):
        self.REPO_FOLDER.mkdir(exist_ok=True)

    def setup(self, git_repo: str = None):
        if not os.listdir(self.REPO_FOLDER):
            self.git_repo_url = git_repo
            self.repo = Repo.clone_from(self.git_repo_url, self.REPO_FOLDER)
            sp.call([f'python3', '-m', 'venv', f'{pathlib.Path(self.REPO_FOLDER / "venv")}'])
            self.install_requirements()

    def destroy(self):
        shutil.rmtree(self.REPO_FOLDER)
        self.REPO_FOLDER.mkdir(exist_ok=True)

    def install_requirements(self):
        if self.PYTHON_INSTANCE.exists():
            sp.call([f'{self.PYTHON_INSTANCE}', '-m', 'pip', 'install', '-r', f'{self.REQ}'])

    def pull(self):
        Repo(self.REPO_FOLDER).remotes.origin.pull()
        self.install_requirements()
