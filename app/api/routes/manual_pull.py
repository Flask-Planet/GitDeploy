from flask import url_for, redirect, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/manual-pull')
@security.login_required('www.login', 'logged_in')
def manual_pull():
    gitdeploy.read_conf()
    if gitdeploy.conf.get("GIT"):

        if not gitdeploy.repo_git_file.exists():
            flash("Git repository not found. Clone it first.")
            return redirect(url_for("www.dashboard"))

        if gitdeploy.update_repo():
            gitdeploy.install_requirements()
            gitdeploy.restart_satellite()
            flash("Changes pulled")
            return redirect(url_for("www.dashboard"))
        else:
            flash("Pull failed, check autogit logs.")
            return redirect(url_for("www.dashboard"))

    else:
        flash("Git is not configured")
        return redirect(url_for("www.dashboard"))
