from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/stop')
@sec.login_required('www.login', 'logged_in')
def stop_app():
    resp = ag.stop_satellite()
    flash(resp)
    return redirect(url_for("www.dashboard"))
