import logging
import subprocess
import sys
import time
from pathlib import Path

from .env import Env
from .resources import generate_supervisor_conf

logging.basicConfig(level=logging.DEBUG)

if not Env.SCONF.exists():
    logging.info("Generating supervisord.conf")
    with open(Env.SCONF, 'w') as f:
        f.write(generate_supervisor_conf(
            ini_location=Env.INILOC
        ))


def launch_supervisord() -> subprocess.Popen:
    process = subprocess.Popen(
        [Path(Env.PYBIN / 'supervisord'), '-c', f'{Path(Env.CWD / "supervisord.conf")}'], cwd=Env.CWD)
    return process


def launch_gunicorn() -> subprocess.CompletedProcess:
    gunicorn_config = Path.cwd() / 'gunicorn.conf.py'
    assert gunicorn_config.exists()

    process = subprocess.run([Path(Env.PYBIN / 'gunicorn')], cwd=Env.CWD, stdout=sys.stdout, stderr=sys.stderr)
    return process


class Launcher:
    def __init__(self):
        Env.INSTANCE.mkdir(exist_ok=True)
        self.supervisord = None
        self.gunicorn = None
        self.supervisord_location = Env.PYBIN / 'supervisord'
        self.gunicorn_location = Env.PYBIN / 'gunicorn'

    def start(self):
        assert self.supervisord_location.exists()
        assert self.gunicorn_location.exists()

        if self.supervisord is None:
            logging.info("Starting supervisord")
            self.supervisord = launch_supervisord()

        while True:
            if Env.SSOCK.exists():
                break
            time.sleep(1)

        logging.info("supervisord started, launching gunicorn...")

        launch_gunicorn()

    def __enter__(self):
        return self.start

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Closing supervisord, please wait...")
        self.supervisord.terminate()

        while True:
            if not Env.SSOCK.exists():
                break
            time.sleep(1)

        exit()
