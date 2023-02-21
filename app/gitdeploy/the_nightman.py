"""fighter of the dayman"""
from time import sleep

import pexpect

from .environment import Environment
from .terminator import terminal_logger


class Supervisorctl:
    def __init__(self):
        self.process = None
        self.before = None
        self.after = None

    def start(self):
        terminal_logger.info("waiting for supervisor.sock")
        while True:
            sleep(1)
            if Environment.supervisord_socket.exists():
                break

        terminal_logger.info("starting supervisorctl")
        self.process = pexpect.spawn("venv/bin/supervisorctl", cwd=Environment.root_dir)

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
