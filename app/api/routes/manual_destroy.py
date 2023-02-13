from flask import url_for, redirect

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/manual-destroy')
@security.login_required('www.login', 'logged_in')
def manual_destroy():
    gitdeploy.stop_satellite()
    gitdeploy.destory_repo()
    return redirect(url_for("www.dashboard"))
