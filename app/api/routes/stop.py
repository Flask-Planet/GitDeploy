from flask import url_for, redirect

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/stop')
@security.login_required('www.login', 'logged_in')
def stop_app():
    gitdeploy.stop_satellite()
    return redirect(url_for("www.dashboard"))
