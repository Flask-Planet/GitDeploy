from flask import session, url_for, redirect

from app.extensions import gitdeploy
from .. import bp


@bp.get('/')
def index():
    gitdeploy.read_conf()
    if gitdeploy.conf.get("FIRST_RUN"):
        return redirect(url_for("www.first_run"))

    if session.get("logged_in"):
        return redirect(url_for("www.dashboard"))
    else:
        return redirect(url_for("www.login"))
