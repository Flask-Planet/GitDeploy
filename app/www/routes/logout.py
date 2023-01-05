from flask import session, url_for, redirect

from .. import bp


@bp.get('/logout')
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("www.login"))
