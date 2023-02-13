from flask import redirect, url_for

from app.extensions import security, gitdeploy, Tools
from .. import bp


@bp.get('/generate-new-secret')
@security.login_required('www.login', 'logged_in')
def generate_new_secret():
    gitdeploy.read_conf()
    gitdeploy.set_conf("WH_SECRET", Tools.generate_random_token(64), write=True)
    return redirect(url_for("www.dashboard"))
