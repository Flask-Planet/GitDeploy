from flask import url_for, redirect, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/manual-install-requirements')
@security.login_required('www.login', 'logged_in')
def manual_install_req():
    if gitdeploy.repo_python.exists():
        if not gitdeploy.repo_requirements_file.exists():
            flash("requirements.txt was not found in repo, add this file to the root of your repo and pull.")
            return redirect(url_for("www.dashboard"))

        gitdeploy.install_requirements()
        flash("Requirements installed.")
        return redirect(url_for("www.dashboard"))

    flash("No python instance found was found in repo, try creating a venv.")
    return redirect(url_for("www.dashboard"))
