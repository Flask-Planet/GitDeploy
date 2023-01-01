from flask import url_for, redirect, flash

from app import ag, sec
from .. import bp


@bp.get('/restart')
@sec.login_required('www.login', 'logged_in')
def restart_app():
    settings = ag.read_settings()
    if not settings['COMMAND']:
        flash('No command set!')
        return redirect(url_for('www.dashboard'))
    ag.restart_satellite()
    return redirect(url_for("www.dashboard"))
