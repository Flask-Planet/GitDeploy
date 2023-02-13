from flask import url_for, redirect, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/manual-create-venv')
@security.login_required('www.login', 'logged_in')
def manual_create_venv():
    if not gitdeploy.repo_python.exists():
        gitdeploy.create_venv()
        flash("Venv created.")
        return redirect(url_for("www.dashboard"))

    flash("Venv already exists.")
    return redirect(url_for("www.dashboard"))

