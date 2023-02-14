from flask import url_for, redirect, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/manual-clone')
@security.login_required('www.login', 'logged_in')
def manual_clone():
    gitdeploy.read_conf()
    if gitdeploy.conf.get("GIT_URL"):
        if gitdeploy.repo_git_file.exists():
            flash("Git repository already exists. Destroy it first.")
            return redirect(url_for("www.dashboard"))

        clone = gitdeploy.clone_repo()
        if clone:
            flash("Repo cloned successfully")
            if not gitdeploy.repo_requirements_file.exists():
                flash("Requirements file not found, add requirements.txt to the root of your repo")
            else:
                gitdeploy.create_venv()
                flash("Virtual environment created")
                gitdeploy.install_requirements()
                flash("Requirements installed")
            return redirect(url_for("www.dashboard"))
        else:
            flash("Could not clone repository, check logs.")
            return redirect(url_for("www.dashboard"))

    else:
        flash("Git is not configured")
        return redirect(url_for("www.dashboard"))
