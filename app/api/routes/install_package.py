from flask import request

from app.extensions import security, gitdeploy, terminator
from .. import bp


@bp.post('/install-package')
@security.login_required('www.login', 'logged_in')
def install_package():
    gitdeploy.read_conf()
    response = {"success": False, "alerts": []}

    if gitdeploy.env.repo_pip.exists():
        install = request.form.get('install')
        if install:
            with terminator(f"venv/bin/pip install", working_directory=gitdeploy.env.repo_dir) as command:
                output = command(install)
                response["success"] = True
                response["alerts"].append(", ".join(output))
                return response

    response["alerts"].append("pip is not installed.")
    return response
