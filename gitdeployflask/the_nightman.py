"""fighter of the dayman"""
import threading
from pathlib import Path
from time import sleep

import pexpect

try:
    from resources import Resources
    from terminator import Terminator, terminal_logger
except ModuleNotFoundError:
    from gitdeployflask.resources import Resources
    from gitdeployflask.terminator import Terminator, terminal_logger

root_dir: Path = Path.cwd()
conf_dir: Path = root_dir / "conf"
supervisor_dir: Path = root_dir / "supervisor"
supervisor_conf: Path = supervisor_dir / "supervisord.conf"
supervisor_sock: Path = supervisor_dir / "supervisor.sock"
supervisor_log: Path = supervisor_dir / "supervisord.log"


class Supervisord(threading.Thread):

    def __init__(self):
        super().__init__()
        supervisor_dir.mkdir(exist_ok=True)
        supervisor_log.touch(exist_ok=True)

        if not supervisor_conf.exists():
            with open(supervisor_conf, "w") as conf:
                conf.write(
                    Resources.generate_supervisor_conf(
                        supervisor_dir=self._remove_cwd(supervisor_dir),
                        log_file=self._remove_cwd(supervisor_log),
                        conf_dir=str(conf_dir),
                    )
                )

    @staticmethod
    def _remove_cwd(path: Path) -> str:
        return str(path).replace(str(root_dir), "").lstrip("/")

    def run(self, *args, **kwargs):
        with Terminator("venv/bin/supervisord", working_directory=root_dir) as run:
            run("-c supervisor/supervisord.conf")


class Gunicorn(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        while True:
            sleep(1)
            if supervisor_sock.exists():
                break

        with Terminator("", working_directory=root_dir) as run:
            output = run("venv/bin/gunicorn")
            for line in output:
                terminal_logger.info(line)


class Supervisorctl:
    def __init__(self):
        self.process = None
        self.before = None
        self.after = None

    def start(self):
        terminal_logger.info("waiting for supervisor.sock")
        while True:
            sleep(1)
            if supervisor_sock.exists():
                break

        terminal_logger.info("starting supervisorctl")
        self.process = pexpect.spawn("venv/bin/supervisorctl -c supervisor/supervisord.conf", cwd=root_dir)
        print("-" * 80)
        print(self.process)
        print("-" * 80)

        while True:
            if self.process.isalive():
                break
        self.process.expect("supervisor> ")
        if isinstance(self.process.after, bytes):
            self.after = self.process.after.decode()

    @property
    def isalive(self):
        return self.process.isalive()

    def stop(self):
        self.process.sendline("shutdown")
        self.process.expect("supervisor> ")
        self.process.sendline("exit")
        self.process.expect(pexpect.EOF)
        self.before = self.process.before
        self.after = self.process.after
        self.process.close()
        self.process = None

    def restart(self):
        self.stop()
        self.start()

    def send(self, line):
        self.process.sendline(line)
        self.process.expect("supervisor> ")
        self.before = self.process.before
        self.after = self.process.after
