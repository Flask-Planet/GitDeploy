from pathlib import Path


def generate_supervisor_conf(
        supervisord_sock: Path,
        supervisord_pid: Path,
        log_file: Path,
        ini_location: Path
):
    return """
[unix_http_server]
file={supervisord_sock}

[supervisord]
logfile={log_file}
logfile_maxbytes=10KB
logfile_backups=0
loglevel=info
pidfile={supervisord_pid}
nodaemon=true
silent=true
minfds=1024
minprocs=200

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://{supervisord_sock}

[include]
files = {ini_location}""".strip().format(**locals())
