from app.extensions import security, gitdeploy, terminator
from .. import bp


@bp.get('/check-packages')
@security.login_required('www.login', 'logged_in')
def check_packages():
    if gitdeploy.repo_python_instance.exists():
        with terminator(
                "venv/bin/pip", working_directory=gitdeploy.repo_dir
        ) as command:
            out, err = command("freeze")
            return out
    else:
        return "No packages installed"
