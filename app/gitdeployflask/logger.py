from datetime import datetime
from pathlib import Path
from typing import Union, Optional


class Logger:
    log_file_path: Path

    def __init__(self):
        pass

    def init_log_file(self, log_file_path: Path):
        self.log_file_path = log_file_path
        if not self.log_file_path.exists():
            self.log_file_path.touch(exist_ok=True)

    def _write(self, output: str):
        with open(self.log_file_path, "a") as f:
            f.write(f"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')} | {output}\n")

    @staticmethod
    def _strip(text: str):
        return text.lstrip(" ").rstrip(" ").rstrip("\n").rstrip("\r").rstrip(",")

    def clear_log(self):
        self.log_file_path.unlink()
        self.log_file_path.touch(exist_ok=True)

    def log(
            self,
            output: Union[str, bytes, list[Union[str, bytes]]],
            remove_str: Optional[list[str]] = None
    ) -> None:

        if isinstance(output, bytes):
            output = output.decode()
            if remove_str:
                for item in remove_str:
                    output = output.replace(item, "")
                self._write(self._strip(output))
                return
            self._write(self._strip(output))
            return

        if isinstance(output, str):
            if remove_str:
                for item in remove_str:
                    output = output.replace(item, "")
                self._write(self._strip(output))
                return
            self._write(self._strip(output))
            return

        if isinstance(output, list):
            for line in output:
                if isinstance(line, bytes):
                    self._write(self._strip(line.decode()))
                else:
                    self._write(self._strip(line))
            return
