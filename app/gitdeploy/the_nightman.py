"""fighter of the dayman"""
from pathlib import Path
from time import sleep

import pexpect

from .environment import Environment
from .terminator import terminal_logger


class Supervisorctl:
    def __init__(self):
        self.process = None
        self.before = None
        self.after = None
        self.supervisord_location = Path(Environment.pybin / 'supervisorctl')
        assert self.supervisord_location.exists()

    def start(self):
        assert Environment.supervisord_socket.exists()

        terminal_logger.info("starting supervisorctl")

        self.process = pexpect.spawn(
            f'{self.supervisord_location} -c supervisord.conf',
            cwd=Environment.root_dir,
            timeout=None,
        )
        while True:
            sleep(0.5)
            if self.process.isalive():
                break

        terminal_logger.info("supervisorctl started")

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
