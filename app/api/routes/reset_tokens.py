from flask import url_for, redirect

from app import ag, sec
from .. import bp


@bp.get('/reset-tokens')
@sec.login_required('www.login', 'logged_in')
def reset_tokens():
    settings = ag.read_settings()
    settings["FIRST_RUN"] = True
    ag.write_settings(settings)
    return redirect(url_for("www.first_run"))
