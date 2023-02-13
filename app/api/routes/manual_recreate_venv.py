from flask import url_for, redirect, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/manual-recreate-venv')
@security.login_required('www.login', 'logged_in')
def manual_recreate_venv():
    gitdeploy.stop_satellite()
    gitdeploy.destroy_venv()
    gitdeploy.create_venv()

    flash("Venv recreated, install requirements if needed.")
    return redirect(url_for("www.dashboard"))
