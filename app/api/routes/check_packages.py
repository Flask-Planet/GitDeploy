from app import ag, sec
from autogit.pip_cli import PipCli
from .. import bp


@bp.get('/check-packages')
@sec.login_required('www.login', 'logged_in')
def check_packages():
    if ag.repo_python_instance.exists():
        with PipCli("freeze", cwd=ag.repo_dir) as output:
            return output
    else:
        return "No packages installed"
