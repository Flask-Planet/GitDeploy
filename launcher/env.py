import sys
from pathlib import Path


class Env:
    CWD = Path.cwd()
    INSTANCE = CWD / 'instance'
    LOGDIR = CWD / 'logs'
    INILOC = CWD / 'instance' / '*.ini'
    SCONF = CWD / 'supervisord.conf'
    SSOCK = CWD / 'supervisor.sock'
    SLOG = CWD / 'supervisor.log'
    SPID = CWD / 'supervisord.pid'
    GPID = CWD / 'gunicorn.pid'
    SYSLOG = LOGDIR / 'gitdeploy.log'

    PYBIN = Path(sys.executable).parent

    def __init__(self):
        if not self.SLOG.exists():
            self.SLOG.touch()
        if not self.INSTANCE.exists():
            self.INSTANCE.mkdir()
        if not self.LOGDIR.exists():
            self.LOGDIR.mkdir()
        if not self.SYSLOG.exists():
            self.SYSLOG.touch()
