import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Environment:
    root_dir: Path = Path.cwd()
    pybin: Path = Path(sys.executable).parent
    instance_dir: Path = root_dir / "instance"
    log_dir = root_dir / "logs"

    log_file: Path = log_dir / "gitdeploy.log"
    conf_file: Path = instance_dir / ".gitdeploy.conf.json"
    supervisord_socket: Path = root_dir / "supervisor.sock"
    satellite_ini: Path = instance_dir / "satellite.ini"

    repo_dir: Path = root_dir / "repo"
    repo_venv_bin: Path = repo_dir / "venv" / "bin"
    repo_python: Path = repo_venv_bin / "python"
    repo_pip: Path = repo_venv_bin / "pip"
    repo_dot_git_folder: Path = repo_dir / ".git"
    repo_dot_git_config: Path = repo_dot_git_folder / "config"
    repo_requirements_file: Path = repo_dir / "requirements.txt"

    conf = dict()
