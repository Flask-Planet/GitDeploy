from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/manual-recreate-venv')
@sec.login_required('www.login', 'logged_in')
def manual_recreate_venv():

    ag.stop_satellite()
    ag.repo_destroy_venv()
    ag.repo_create_venv()

    flash("Venv recreated, install requirements if needed.")
    return redirect(url_for("www.dashboard"))

