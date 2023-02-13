from flask import render_template, request

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/logs')
@security.login_required('www.login', 'logged_in')
def logs():
    if request.args.get('clear', False):
        gitdeploy.get_sattelite_log()
    return render_template(
        bp.tmpl("logs.html"),
        gitdeploy_logs=gitdeploy.read_gitdeploy_log()
    )
