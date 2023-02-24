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


def write_gunicorn_pid(pid):
    with open(Env.GPID, 'w') as pid_file:
        pid_file.write(str(pid))


def launch_supervisord() -> subprocess.Popen:
    process = subprocess.Popen(
        [Path(Env.PYBIN / 'supervisord'), '-c', f'{Path(Env.CWD / "supervisord.conf")}'], cwd=Env.CWD)
    return process


def launch_gunicorn(background_task: bool = False):
    gunicorn_config = Path.cwd() / 'gunicorn.conf.py'
    assert gunicorn_config.exists()
    if not background_task:
        process = subprocess.Popen([Path(Env.PYBIN / 'gunicorn')], cwd=Env.CWD, stdout=sys.stdout, stderr=sys.stderr)
        write_gunicorn_pid(process.pid)
        process.communicate()

    process = subprocess.Popen(
        [Path(Env.PYBIN / 'gunicorn')],
        cwd=Env.CWD,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    write_gunicorn_pid(process.pid)
    logging.info("Gunicorn started, running in background...")


class Launcher:
    def __init__(self):
        Env.INSTANCE.mkdir(exist_ok=True)
        self.supervisord = None
        self.gunicorn = None
        self.supervisord_location = Env.PYBIN / 'supervisord'
        self.gunicorn_location = Env.PYBIN / 'gunicorn'

    def start(self, background_task: bool = False):
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

        launch_gunicorn(background_task=background_task)

    @staticmethod
    def stop():
        if not Env.SPID.exists():
            logging.info("No supervisord process found, skipping...")
        else:
            logging.info("Stopping supervisord...")
            with open(Env.SPID) as supervisor_pid_file:
                pid = supervisor_pid_file.read()
                subprocess.run(f"kill -15 {pid}", shell=True)

        if not Env.GPID.exists():
            logging.info("No gunicorn process found, skipping...")
        else:
            logging.info("Stopping gunicorn...")
            with open(Env.GPID) as gunicorn_pid_file:
                pid = gunicorn_pid_file.read()
                subprocess.run(f"kill -15 {pid}", shell=True)
            Env.GPID.unlink()

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
