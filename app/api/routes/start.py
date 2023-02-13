from flask import url_for, redirect, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/start')
@security.login_required('www.login', 'logged_in')
def start_app():
    gitdeploy.read_conf()
    if not gitdeploy.conf.get('COMMAND'):
        flash('No command set!')
        return redirect(url_for('www.dashboard'))
    gitdeploy.start_satellite()
    return redirect(url_for("www.dashboard"))
