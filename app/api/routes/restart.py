from flask import url_for, redirect, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/restart')
@security.login_required('www.login', 'logged_in')
def restart_app():
    gitdeploy.read_conf()
    if not gitdeploy.conf.get('COMMAND'):
        flash('No command set!')
        return redirect(url_for('www.dashboard'))
    gitdeploy.restart_satellite()
    return redirect(url_for("www.dashboard"))
