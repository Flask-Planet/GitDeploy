from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/manual-pull')
@sec.login_required('www.login', 'logged_in')
def manual_pull():
    settings = ag.read_settings()
    if settings["GIT"]:
        if not ag.repo_dir.exists():
            flash("Git repository not found. Clone it first.")
            return redirect(url_for("www.dashboard"))

        if ag.repo_pull():
            flash("Changes pulled")
            return redirect(url_for("www.dashboard"))
        else:
            flash("Pull failed, check autogit logs.")
            return redirect(url_for("www.dashboard"))

    else:
        flash("Git is not configured")
        return redirect(url_for("www.dashboard"))
