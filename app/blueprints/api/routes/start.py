from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/start')
@sec.login_required('www.login', 'logged_in')
def start_app():
    resp = ag.start_satellite()
    flash(resp)
    return redirect(url_for("www.dashboard"))
