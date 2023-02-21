# ## From environment.py:
#
# def _process_os_release(terminal_output: list):
#     distro = None
#     version = None
#     for line in terminal_output:
#         if "PRETTY_NAME" in line:
#             value = line.replace('"', '').split("=")[1]
#             distro = value.split(" ")[0].lower()
#         if "VERSION_ID" in line:
#             value = line.replace('"', '').split("=")[1]
#             version = value
#         if "ProductName" in line:
#             value = line.replace('\t', '').split(":")[1]
#             distro = value.lower()
#         if "ProductVersion" in line:
#             value = line.replace('\t', '').split(":")[1]
#             version = value.lower()
#
#     return distro, version
#
# class DebianEnv:
#     distro = "Debian"
#     version: str
#     package_manager = "apt"
#     user: str
#
#     def __init__(self, version: str):
#         self.version = version
#         self.user = os.getlogin()
#
#     def __repr__(self):
#         return f"<DebianEnv {self.distro} {self.version}>"
#
#     def __str__(self):
#         return f"{self.distro} {self.version}"
#
#
# class UbuntuEnv:
#     distro = "Ubuntu"
#     version: str
#     package_manager = "apt"
#     user: str
#
#     def __init__(self, version: str):
#         self.version = version
#         self.user = os.getlogin()
#
#     def __repr__(self):
#         return f"<UbuntuEnv {self.distro} {self.version}>"
#
#     def __str__(self):
#         return f"{self.distro} {self.version}"
#
#
# class AlpineEnv:
#     distro = "Alpine"
#     version: str
#     package_manager = "apk"
#     user: str
#
#     def __init__(self, version: str):
#         self.version = version
#         self.user = os.getlogin()
#
#     def __repr__(self):
#         return f"<AlpineEnv {self.distro} {self.version}>"
#
#     def __str__(self):
#         return f"{self.distro} {self.version}"
#
#
# class MacosEnv:
#     distro = "MacOS"
#     version: str
#     package_manager = "brew"
#     user: str
#
#     def __init__(self, version: str):
#         self.version = version
#         self.user = os.getlogin()
#
#     def __repr__(self):
#         return f"<MacosEnv {self.distro} {self.version}>"
#
#     def __str__(self):
#         return f"{self.distro} {self.version}"
#
#
# os: t.Optional[t.Union[DebianEnv, UbuntuEnv, AlpineEnv, MacosEnv]] = None


# def _check_env(self):
#     compatible_os = {
#         "debian": ["10", "11"],
#         "ubuntu": ["18.04", "20.04", "22.04", "22.10", "23.04"],
#         "alpine": ["3.14", "3.15", "3.16", "3.17"],
#         "macos": ["12.6.3"],
#     }
#
#     base_cmd = None if sys.platform == 'darwin' else "cat"
#     command_name = "sw_vers" if sys.platform == 'darwin' else "/etc/os-release"
#     without_base = True if sys.platform == 'darwin' else False
#
#     with Terminator(base_cmd, log=False) as command:
#         distro, version = _process_os_release(
#             command(command_name, without_base))
#
#         if distro not in compatible_os:
#             raise Exception(
#                 f"{distro} is not a compatible operating system. "
#                 f"Please use one of the following: {compatible_os.keys()}"
#             )
#
#         if version not in compatible_os[distro]:
#             os_needed = ""
#             for key, value in compatible_os.items():
#                 os_needed += f"\n{key.capitalize()}"
#                 for v in value:
#                     os_needed += f" {v}"
#             raise Exception(
#                 f"{distro} {version} is not a compatible operating system. "
#                 f"\nPlease use one of the following:{os_needed}"
#             )
#
#     self.os = getattr(self, f"{distro.capitalize()}Env")(version)


## from __main__.py
#
#
# from time import sleep
#
# try:
#     from environment import Environment
#     from the_nightman import Supervisord, Gunicorn, supervisor_sock
# except ImportError:
#     from .environment import Environment
#     from .the_nightman import Supervisord, Gunicorn, supervisor_sock
#
#
# class Launcher:
#     def __init__(self):
#         self.env = Environment()
#         self.supervisord = Supervisord()
#         self.gunicorn = Gunicorn()
#
#     def __enter__(self):
#         self.supervisord.start()
#         while True:
#             sleep(1)
#             if supervisor_sock.exists():
#                 break
#         self.gunicorn.start()
#         return "Running on: 0.0.0.0:9898 (Press Ctrl+C to stop)"
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         pass
#
#
# if __name__ == '__main__':
#     with Launcher() as output:
#         print(output)


# def _failed(outputs: t.List[str], fail_on: t.List[str] = None):
#     complete = ""
#     for output in outputs:
#         complete += output
#
#     for fail in fail_on:
#         if fail in complete:
#             return True
#     return False
#


## from logger.py
#
# from datetime import datetime
# from pathlib import Path
# from typing import Union, Optional
#
#
# class Logger:
#     log_file_path: Path
#
#     def __init__(self):
#         pass
#
#     def init_log_file(self, log_file_path: Path):
#         self.log_file_path = log_file_path
#         if not self.log_file_path.exists():
#             self.log_file_path.touch(exist_ok=True)
#
#     def _write(self, output: str):
#         with open(self.log_file_path, "a") as f:
#             f.write(f"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')} | {output}\n")
#
#     @staticmethod
#     def _strip(text: str):
#         return text.lstrip(" ").rstrip(" ").rstrip("\n").rstrip("\r").rstrip(",")
#
#     def clear_log(self):
#         self.log_file_path.unlink()
#         self.log_file_path.touch(exist_ok=True)
#
#     def log(
#             self,
#             output: Union[str, bytes, list[Union[str, bytes]]],
#             remove_str: Optional[list[str]] = None
#     ) -> None:
#
#         if isinstance(output, bytes):
#             output = output.decode()
#             if remove_str:
#                 for item in remove_str:
#                     output = output.replace(item, "")
#                 self._write(self._strip(output))
#                 return
#             self._write(self._strip(output))
#             return
#
#         if isinstance(output, str):
#             if remove_str:
#                 for item in remove_str:
#                     output = output.replace(item, "")
#                 self._write(self._strip(output))
#                 return
#             self._write(self._strip(output))
#             return
#
#         if isinstance(output, list):
#             for line in output:
#                 if isinstance(line, bytes):
#                     self._write(self._strip(line.decode()))
#                 else:
#                     self._write(self._strip(line))
#             return
