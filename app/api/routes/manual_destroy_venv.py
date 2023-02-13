from flask import url_for, redirect, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/manual-destroy-venv')
@security.login_required('www.login', 'logged_in')
def manual_destroy_venv():
    gitdeploy.stop_satellite()
    gitdeploy.destroy_venv()
    flash("Venv destroyed")
    return redirect(url_for("www.dashboard"))
