from flask import render_template

from app import ag, sec
from .. import bp


@bp.get('/app-logs')
@sec.login_required('www.login', 'logged_in')
def app_logs():
    return render_template(
        bp.tmpl("app_logs.html"),
        satellite_logs=ag.read_satellite_log()
    )
