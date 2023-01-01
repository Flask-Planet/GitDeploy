from flask import redirect, url_for

from app import ag, sec
from .. import bp
from autogit.tools import Tools


@bp.get('/generate-new-secret')
@sec.login_required('www.login', 'logged_in')
def generate_new_secret():
    settings = ag.read_settings()
    settings["WH_SECRET"] = Tools.generate_random_token(64)
    ag.write_settings(settings)
    return redirect(url_for("www.dashboard"))
