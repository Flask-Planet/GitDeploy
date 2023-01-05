import os
from dataclasses import dataclass
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


@dataclass
class Resources:
    autogit_settings = {
        "AUTOGIT_SK": _wash_none_env(os.getenv("AUTOGIT_SK")),
        "GIT": None,
        "GIT_BRANCH": os.environ.get("AUTOGIT_GIT_BRANCH", "master"),
        "GIT_PRIVATE": _wash_bool_env(os.environ.get("AUTOGIT_GIT_PRIVATE")),
        "GIT_URL": _wash_none_env(os.getenv("AUTOGIT_GIT_URL")),
        "GIT_USERNAME": _wash_none_env(os.getenv("AUTOGIT_GIT_TOKEN_NAME")),
        "GIT_PASSWORD": _wash_none_env(os.getenv("AUTOGIT_GIT_TOKEN")),
        "COMMAND": _wash_none_env(os.getenv("AUTOGIT_COMMAND")),
        "APP_STATE": False,
        "WH_ENABLED": _wash_bool_env(os.environ.get("AUTOGIT_WEBHOOK_ENABLED")),
        "WH_SECRET": os.getenv("AUTOGIT_WEBHOOK_SECRET", Tools.generate_random_token(64)),
        "FIRST_RUN": True,
        "T1": Tools.generate_random_token(24),
        "T2": Tools.generate_random_token(24),
    }

    supervisor_config = """
[unix_http_server]
file=/run/supervisord.sock

[supervisord]
logfile=/var/log/supervisord.log

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///run/supervisord.sock

[include]
files = {config_includes_path}/*.ini
    """.strip()

    supervisor_ini: str = """
[program:{app}]
directory={working_directory}
command={command}
user=root
autostart={autostart}
autorestart={autorestart}
stdout_logfile={log_location}
stderr_logfile={log_location}
            """.strip()
