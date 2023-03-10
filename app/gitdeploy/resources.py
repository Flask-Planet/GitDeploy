import os
from pathlib import Path
from typing import Union

from .tools import Tools


def _wash_none_env(env: Union[None, str]) -> Union[None, str, bool]:
    none_markers = ["none", "null", "nil"]
    if isinstance(env, str):
        if env.lower() in none_markers:
            return None
        else:
            return env
    return None


def _wash_bool_env(env: Union[None, str]) -> Union[None, str, bool]:
    true_markers = ["true", "1", "yes", "on"]
    if isinstance(env, str):
        if env.lower() in true_markers:
            return True
    else:
        return False


class Resources:

    @staticmethod
    def generate_default_conf():
        return {
            "GD_SK": _wash_none_env(os.getenv("GD_SK")),
            "GIT": '',
            "GIT_BRANCH": os.environ.get("GD_GIT_BRANCH", "master"),
            "GIT_PRIVATE": _wash_bool_env(os.environ.get("GD_GIT_PRIVATE")),
            "GIT_URL": _wash_none_env(os.getenv("GD_GIT_URL", '')),
            "GIT_TOKEN_NAME": _wash_none_env(os.getenv("GD_GIT_TOKEN_NAME")),
            "GIT_TOKEN": _wash_none_env(os.getenv("GD_GIT_TOKEN")),
            "COMMAND": _wash_none_env(os.getenv("GD_COMMAND", '')),
            "APP_AUTO_START": _wash_bool_env(os.environ.get("GD_APP_AUTO_START", False)),
            "APP_STATE": False,
            "WH_ENABLED": _wash_bool_env(os.environ.get("GD_WEBHOOK_ENABLED")),
            "WH_SECRET": os.getenv("GD_WEBHOOK_SECRET", Tools.generate_random_token(64)),
            "FIRST_RUN": True,
            "T1": Tools.generate_random_token(24),
            "T2": Tools.generate_random_token(24),
        }

    @staticmethod
    def generate_satellite_ini(
            app: str,
            command: Path,
            log_location: Path,
            working_directory: Path,
    ) -> str:
        return """
[program:{app}]
directory={working_directory}
command={command}
autostart=false
autorestart=false
startretries=0
stdout_logfile={log_location}
stderr_logfile={log_location}
""".strip().format(**locals())
