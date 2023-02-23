from pathlib import Path


def generate_supervisor_conf(
        ini_location: Path
):
    return """
[unix_http_server]
file=supervisor.sock

[supervisord]
logfile=supervisor.log
logfile_maxbytes=10KB
logfile_backups=0
loglevel=info
pidfile=supervisor.pid
nodaemon=true
silent=true
minfds=1024
minprocs=200

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://supervisor.sock

[include]
files = {ini_location}""".strip().format(**locals())
