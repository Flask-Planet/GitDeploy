from flask import render_template, request

from app import ag, sec
from .. import bp


@bp.get('/autogit-logs')
@sec.login_required('www.login', 'logged_in')
def autogit_logs():
    if request.args.get('clear', False):
        ag.del_autogit_log()
    return render_template(
        bp.tmpl("autogit_logs.html"),
        autogit_logs=ag.read_autogit_log()
    )
