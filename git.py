import os
import pathlib
import subprocess as sp

from git import Repo

from dotenv import load_dotenv
from flask import Flask


class SatelliteAppController:
    process: sp.Popen = None

    def start(self):
        self.process = sp.Popen(
            ['venv/bin/gunicorn', '-b', '0.0.0.0:5000', 'run:sgi'],
            cwd=pathlib.Path(pathlib.Path.cwd() / "repo"),
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )

    def stop(self):
        if hasattr(self.process, 'send_signal'):
            sp.Popen.terminate(self.process)


class AppController:
    satellite_app: SatelliteAppController()

    def __init__(self, create_flask_app):
        self.create_flask_app = create_flask_app
        self.satellite_app = SatelliteAppController()

    def __enter__(self):
        return self.create_flask_app(self.satellite_app)

    def __exit__(self, type_, value, traceback):
        self.satellite_app.stop()


class Github:
    github_repo_url: str
    repo_folder: pathlib.Path
    repo: Repo

    def __init__(self, github_repo: str):
        self.github_repo_url = github_repo
        self.repo_folder = pathlib.Path(pathlib.Path.cwd() / "repo")
        self.repo_folder.mkdir(exist_ok=True)

    def setup(self):
        if len(os.listdir(self.repo_folder)) == 0:
            self.repo = Repo.clone_from(self.github_repo_url, self.repo_folder)
            sp.call([f'python3', '-m', 'venv', f'{self.repo_folder}/venv'])
            sp.call([f'{self.repo_folder}/venv/bin/python3', '-m', 'pip', 'install', '-r',
                     f'{self.repo_folder}/requirements.txt'])

    def pull(self):
        Repo(self.repo_folder).remotes.origin.pull()


load_dotenv()

git = os.getenv("GIT")


def create_app(satellite_app):
    app = Flask(__name__)

    github = Github(git)
    github.setup()

    satellite_app.start()

    # Index
    @app.get('/pull')
    def webhook():
        github.pull()
        return 'pulled', 200

    @app.get('/start')
    def start_app():
        satellite_app.start()
        return 'started', 200

    @app.get('/stop')
    def stop_app():
        satellite_app.stop()
        return 'stopped', 200

    return app


if __name__ == "__main__":
    with AppController(create_app) as app:
        app.run(port=5500, host="0.0.0.0")
