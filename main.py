import os
from pathlib import Path

from autogit.supervisor import Supervisor, SupervisorIni
from autogit.terminal import Terminal


def setup_env():
    port = os.getenv("GD_PORT")
    workers = os.getenv("GD_WORKERS")
    cwd = os.getenv("GD_CWD")

    if not port:
        os.environ["GD_PORT"] = "5500"

    if not workers:
        os.environ["GD_WORKERS"] = "3"

    if not cwd:
        os.environ["GD_CWD"] = "/autogit"


def setup_folders():
    cwd = Path(os.getenv("GD_CWD"))

    working_dir = cwd
    log_dir = working_dir / "logs"
    config_dir = working_dir / "config"
    repo_dir = working_dir / "repo"

    directories = [
        log_dir,
        config_dir,
        repo_dir,
    ]

    for directory in directories:
        directory.mkdir(exist_ok=True)


def setup_supervisor():
    port = os.getenv("GD_PORT")
    workers = os.getenv("GD_WORKERS")

    supervisor = Supervisor(
        supervisor_config="/etc/supervisord.conf",
        config_includes_path="/autogit/config"
    )
    autogit_ini = SupervisorIni(
        path=Path("/autogit/config/autogit.ini"),
        app="autogit",
        working_directory="/autogit",
        command=f"gunicorn -b 0.0.0.0:{port} -w {workers} run:sgi",
        autostart=True,
        autorestart=True,
        log_location="/autogit/logs/autogit.log"
    )
    supervisor.setup()
    supervisor.write_init(autogit_ini)


setup_env()
setup_folders()
setup_supervisor()

with Terminal("ip address") as output:
    print(output)

with Terminal("supervisord --nodaemon --configuration /etc/supervisord.conf") as output:
    print(output)
