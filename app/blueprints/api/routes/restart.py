from flask import url_for, redirect

from app import ag, sec
from .. import bp


@bp.get('/restart')
@sec.login_required('www.login', 'logged_in')
def restart_app():
    ag.restart_satellite()
    return redirect(url_for("www.dashboard"))
