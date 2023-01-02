from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/manual-destroy-venv')
@sec.login_required('www.login', 'logged_in')
def manual_destroy_venv():

    ag.stop_satellite()
    ag.repo_destroy_venv()

    flash("Venv destroyed")
    return redirect(url_for("www.dashboard"))

