from dataclasses import dataclass

from .tools import Tools


@dataclass
class Resources:
    autogit_settings = {
        "AUTOGIT_SK": None,
        "GIT": None,
        "GIT_PRIVATE": False,
        "GIT_URL": None,
        "GIT_USERNAME": None,
        "GIT_PASSWORD": None,
        "COMMAND": None,
        "APP_STATE": False,
        "WH_SECRET": Tools.generate_random_token(64),
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
