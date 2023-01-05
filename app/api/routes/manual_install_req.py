from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/manual-install-requirements')
@sec.login_required('www.login', 'logged_in')
def manual_install_req():
    if ag.repo_python_instance.exists():

        if not ag.repo_requirements.exists():
            flash("requirements.txt was not found in repo, add this file to the root of your repo and pull.")
            return redirect(url_for("www.dashboard"))

        ag.repo_install_requirements()
        flash("Requirements installed.")
        return redirect(url_for("www.dashboard"))

    flash("No python instance found was found in repo, try creating a venv.")
    return redirect(url_for("www.dashboard"))
