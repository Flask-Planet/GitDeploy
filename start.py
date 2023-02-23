import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

CWD = Path.cwd()
INSTANCE = CWD / 'instance'
SOCKET = INSTANCE / 'supervisor.sock'
PYBIN = Path(sys.executable).parent

# this is an attempt to try and stop conflicts between the main app and the satellite app
VERSION_SIG = '8cc331ae4b'

# These should reflect the values in app/default.config.toml
os.environ[f"INSTANCE_TAG_{VERSION_SIG}"] = f"gitdeploy_{os.urandom(24).hex()}"
os.environ[f"SECRET_KEY_{VERSION_SIG}"] = os.urandom(24).hex()
os.environ[f"SESSION_{VERSION_SIG}"] = f"session_{os.urandom(24).hex()}"


def launch_supervisord() -> subprocess.Popen:
    process = subprocess.Popen([Path(PYBIN / 'supervisord'), '-c', 'supervisord.conf'], cwd=CWD)
    return process


def launch_gunicorn() -> subprocess.CompletedProcess:
    gunicorn_config = Path.cwd() / 'gunicorn.conf.py'
    assert gunicorn_config.exists()

    process = subprocess.run([Path(PYBIN / 'gunicorn')], cwd=CWD, stdout=sys.stdout, stderr=sys.stderr)
    return process


class Launcher:
    def __init__(self):
        INSTANCE.mkdir(exist_ok=True)
        self.supervisord = None
        self.gunicorn = None
        self.supervisord_location = PYBIN / 'supervisord'
        self.gunicorn_location = PYBIN / 'gunicorn'

    def start(self):
        assert self.supervisord_location.exists()
        assert self.gunicorn_location.exists()

        if self.supervisord is None:
            logging.info("Starting supervisord")
            self.supervisord = launch_supervisord()

        while True:
            if SOCKET.exists():
                break
            time.sleep(1)

        logging.info("Starting supervisord")

        launch_gunicorn()

    def __enter__(self):
        return self.start

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Closing supervisord, please wait...")
        self.supervisord.terminate()

        while True:
            if not SOCKET.exists():
                break
            time.sleep(1)

        exit()


with Launcher() as start:
    start()
