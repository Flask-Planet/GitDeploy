from flask import session, url_for, redirect

from app import ag
from .. import bp


@bp.get('/')
def index():
    settings = ag.read_settings()
    if not settings.get("FIRST_RUN"):
        return redirect(url_for("www.first_run"))

    if session.get("logged_in"):
        return redirect(url_for("www.dashboard"))
    else:
        return redirect(url_for("www.login"))
