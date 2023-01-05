from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/manual-create-venv')
@sec.login_required('www.login', 'logged_in')
def manual_create_venv():
    if ag.repo_create_venv():
        flash("Venv created.")
        return redirect(url_for("www.dashboard"))

    flash("Venv already exists.")
    return redirect(url_for("www.dashboard"))

