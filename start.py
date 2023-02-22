import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

CWD = Path.cwd()
INSTANCE = CWD / 'instance'
SOCKET = INSTANCE / 'supervisor.sock'
PYBIN = Path(sys.executable).parent


class Launcher:
    def __init__(self):
        INSTANCE.mkdir(exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.supervisord = None
        self.gunicorn = None
        self.supervisord_location = PYBIN / 'supervisord'
        self.gunicorn_location = PYBIN / 'gunicorn'

    def start(self):
        assert self.supervisord_location.exists()
        assert self.gunicorn_location.exists()

        self.supervisord = self.executor.submit(launch_supervisord).result()
        while True:
            if SOCKET.exists():
                break
            time.sleep(1)

        self.gunicorn = self.executor.submit(launch_gunicorn).result()

    def __enter__(self):
        return self.start

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.supervisord.terminate()

        while True:
            if not SOCKET.exists():
                break
            time.sleep(1)

        exit()


def launch_supervisord():
    process = subprocess.Popen([Path(PYBIN / 'supervisord'), '-c', 'supervisord.conf'], cwd=CWD)
    return process


def launch_gunicorn():
    gunicorn_config = Path.cwd() / 'gunicorn.conf.py'
    assert gunicorn_config.exists()

    process = subprocess.run([Path(PYBIN / 'gunicorn')], cwd=CWD, stdout=sys.stdout, stderr=sys.stderr)
    return process


with Launcher() as start:
    start()
