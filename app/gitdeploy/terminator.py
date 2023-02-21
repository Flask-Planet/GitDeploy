import io
import logging
import subprocess
import typing as t
from pathlib import Path

import pexpect

from .environment import Environment

Environment.log_dir.mkdir(exist_ok=True)
Environment.log_file.touch(exist_ok=True)

terminal_logger = logging.getLogger("terminal")
terminal_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M')

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler(Environment.log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

terminal_logger.addHandler(file_handler)
terminal_logger.addHandler(stdout_handler)


class Terminator:
    base: t.Optional[str]
    working_directory: t.Optional[Path]
    traceback: t.Optional[dict]
    print_output: bool

    class Popen:
        def __init__(
                self,
                command: str,
                working_directory: t.Optional[Path] = None,
                log: bool = True
        ):
            self.command = command.split(" ")
            self.cwd = working_directory or Path.cwd()
            self.process = None
            self.output_lines = []
            self.log = log

        def __enter__(self) -> list:
            self.process = subprocess.Popen(
                args=self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd
            )

            for line in io.TextIOWrapper(self.process.stdout, encoding="utf-8"):
                self.output_lines.append(line.strip())
                if self.log:
                    terminal_logger.info(line.strip())

            for line in io.TextIOWrapper(self.process.stderr, encoding="utf-8"):
                self.output_lines.append(line.strip())
                if self.log:
                    terminal_logger.error(line.strip())

            return self.output_lines

        def __exit__(self, exc_type, exc_value, traceback):
            self.process.terminate()
            self.command = None
            self.process = None
            self.output_lines = None

    class CheckOutput:
        def __init__(
                self,
                command: str,
                working_directory: t.Optional[Path] = None,
                log: bool = True
        ):
            self.command = command.split(" ")
            self.cwd = working_directory or Path.cwd()
            self.process = None
            self.log = log

        def __enter__(self) -> list:
            output = subprocess.run(
                self.command,
                stderr=subprocess.STDOUT,
            )
            return [output]

        def __exit__(self, exc_type, exc_value, traceback):
            self.command = None
            self.process = None

    def __init__(
            self,
            base: t.Optional[str] = None,
            type_: str = "popen",
            working_directory: t.Optional[Path] = None,
            print_output: bool = False,
            log: bool = True,
    ):
        """
        :type_
            popen: subprocess.Popen [DEFAULT]
            check_output: subprocess.check_output
            pexpect: pexpect.spawn
        """
        self.base = base
        self.type_ = type_
        self.working_directory = working_directory or Path.cwd()
        self.traceback = dict()
        self.print_output = print_output
        self.log = log

    def __enter__(self) -> t.Callable:
        if self.type_ == "check_output":
            return self._check_output
        if self.type_ == "pexpect":
            return self._pexpect

        return self._popen

    def __exit__(self, exc_type, exc_value, traceback):
        self.base = None
        self.working_directory = None
        self.traceback = None

    def _popen(
            self,
            command: t.Union[str, list],
            working_directory: t.Optional[Path] = None,
            without_base: bool = False,
    ) -> list:
        if isinstance(command, list):
            command = " ".join(command)

        if without_base:
            command = command

        else:
            if self.base:
                command = f"{self.base} {command}"

        if working_directory:
            self.working_directory = working_directory

        with self.Popen(command, working_directory=self.working_directory, log=self.log) as result:
            self.traceback.update(
                {len(self.traceback): (command, result)}
            )
            return result

    def _check_output(
            self,
            command: t.Union[str, list],
            working_directory: t.Optional[Path] = None,
            without_base: bool = False,
    ) -> list:
        if isinstance(command, list):
            command = " ".join(command)

        if without_base:
            command = command

        else:
            if self.base:
                command = f"{self.base} {command}"

        if working_directory:
            self.working_directory = working_directory

        with self.CheckOutput(command, working_directory=self.working_directory, log=self.log) as result:
            self.traceback.update(
                {len(self.traceback): (command, result)}
            )
            return result

    def _pexpect(
            self,
            command: t.Union[str, list],
            expects: t.Optional[dict] = None,
            working_directory: t.Optional[Path] = None,
            without_base: bool = False,
    ) -> list:
        if isinstance(command, list):
            command = " ".join(command)

        if without_base:
            command = command

        else:
            if self.base:
                command = f"{self.base} {command}"

        if working_directory:
            self.working_directory = working_directory

        child = pexpect.spawn(
            command,
            timeout=60,
            cwd=self.working_directory,
        )
        output_lines = []

        for key, value in expects.items():
            child.expect([key, pexpect.EOF])
            if value is None:
                if child.isalive():
                    child.close()
            else:
                child.sendline(value.encode('utf-8'))

        if isinstance(child.before, bytes):
            before = child.before.decode('utf-8')
            terminal_logger.info(before)
            output_lines.append(before)
        if isinstance(child.after, bytes):
            after = child.after.decode('utf-8')
            if "Username" in after:
                after = "Git repository is private."
            terminal_logger.info(after)
            output_lines.append(after)

        return output_lines
