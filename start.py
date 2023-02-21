import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

CWD = Path.cwd()
SOCKET = Path.cwd() / 'instance' / 'supervisor.sock'


class Launcher:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.supervisord = None
        self.gunicorn = None

    def start(self):
        self.supervisord = self.executor.submit(launch_supervisord).result()
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
    process = subprocess.Popen(['venv/bin/supervisord'], cwd=CWD)
    return process


def launch_gunicorn():
    gunicorn_config = Path.cwd() / 'gunicorn.conf.py'
    assert gunicorn_config.exists()

    process = subprocess.run(['venv/bin/gunicorn'], cwd=CWD, stdout=sys.stdout, stderr=sys.stderr)
    return process


with Launcher() as start:
    start()
