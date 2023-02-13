from flask import url_for, redirect

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/reset-tokens')
@security.login_required('www.login', 'logged_in')
def reset_tokens():
    gitdeploy.set_conf("FIRST_RUN", True, write=True)
    return redirect(url_for("www.first_run"))
