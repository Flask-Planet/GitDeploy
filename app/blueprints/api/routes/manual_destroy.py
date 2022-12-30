from flask import url_for, redirect

from app import ag, sec
from .. import bp


@bp.get('/manual-destroy')
@sec.login_required('www.login', 'logged_in')
def manual_destroy():
    ag.repo_destroy()
    return redirect(url_for("www.dashboard"))
