from flask import url_for, redirect

from app import ag, sec
from .. import bp


@bp.get('/start')
@sec.login_required('www.login', 'logged_in')
def start_app():
    ag.start_satellite()
    return redirect(url_for("www.dashboard"))
