import subprocess
import typing as t
from pathlib import Path


class Terminator:
    base: t.Optional[str]
    working_directory: t.Optional[Path]
    traceback: t.Optional[dict]
    print_output: bool

    class TerminatorProcess:
        def __init__(self, command: str, working_directory: t.Optional[Path] = None):
            self.command = command.split(" ")
            self.cwd = working_directory or Path.cwd()
            self.process = None

        def __enter__(self) -> tuple[str, str]:
            self.process = subprocess.Popen(
                args=self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd
            )

            self.process.stdin.close()

            return self.process.stdout.read().decode(), self.process.stderr.read().decode()

        def __exit__(self, exc_type, exc_value, traceback):
            self.process.terminate()

    def __init__(
            self,
            base: t.Optional[str] = None,
            working_directory: t.Optional[Path] = None,
            print_output: bool = False
    ):
        self.base = base
        self.cwd = working_directory or Path.cwd()
        self.traceback = dict()
        self.print_output = print_output

    def __enter__(self) -> t.Callable:
        return self._do

    def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
    ):
        self.base = None
        self.working_directory = None
        self.traceback = None

    def _do(
            self,
            command: t.Union[str, list],
            working_directory: t.Optional[Path] = None,
            without_base: bool = False
    ) -> any:
        if isinstance(command, list):
            command = " ".join(command)

        if without_base:
            command = command

        else:
            if self.base:
                command = f"{self.base} {command}"

        if working_directory:
            self.working_directory = working_directory

        with self.TerminatorProcess(command, working_directory=self.cwd) as result:
            self.traceback.update(
                {len(self.traceback): (command, result)}
            )
            if self.print_output:
                if result[0]:
                    print(result[0])
                if result[1]:
                    print(result[1])
            return result

    def call(
            self,
            command: t.Union[str, list],
            working_directory: t.Optional[Path] = None,
            without_base: bool = False
    ) -> any:
        return self._do(command, working_directory, without_base)
