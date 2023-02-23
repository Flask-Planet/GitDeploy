import sys
from pathlib import Path


class Env:
    CWD = Path.cwd()
    INSTANCE = CWD / 'instance'
    INILOC = CWD / 'instance' / '*.ini'
    SCONF = CWD / 'supervisord.conf'
    SSOCK = CWD / 'supervisor.sock'
    SPID = CWD / 'supervisor.pid'
    SLOG = CWD / 'supervisor.log'

    PYBIN = Path(sys.executable).parent
