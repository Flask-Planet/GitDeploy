from pathlib import Path

from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/manual-clone')
@sec.login_required('www.login', 'logged_in')
def manual_clone():
    settings = ag.read_settings()
    if settings["GIT"]:
        if Path(ag.repo_dir / ".git").exists():
            flash("Git repository already exists. Destroy it first.")
            return redirect(url_for("www.dashboard"))

        clone = ag.repo_clone(settings["GIT"])
        if clone:
            flash("Repo cloned successfully")
            if not ag.repo_requirements.exists():
                flash("Requirements file not found, add requirements.txt to the root of your repo")
            else:
                flash("Requirements installed")
                ag.repo_create_venv()
                ag.repo_install_requirements()
            return redirect(url_for("www.dashboard"))
        else:
            flash("Could not clone repository, check logs.")
            return redirect(url_for("www.dashboard"))

    else:
        flash("Git is not configured")
        return redirect(url_for("www.dashboard"))
