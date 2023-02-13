from flask import session, url_for, redirect

from app.extensions import gitdeploy
from .. import bp


@bp.get('/')
def index():
    gitdeploy.read_conf()
    if not gitdeploy.conf.get("FIRST_RUN"):
        return redirect(url_for("www.first_run"))

    if gitdeploy.conf.get("logged_in"):
        return redirect(url_for("www.dashboard"))
    else:
        return redirect(url_for("www.login"))
