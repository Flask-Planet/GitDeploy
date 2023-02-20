from flask import url_for, redirect, request, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.post('/save/command')
@security.login_required('www.login', 'logged_in')
def save_command():
    gitdeploy.read_conf()
    gitdeploy.set_conf('COMMAND', request.form.get("command", None), write=True)
    gitdeploy.write_satellite_ini()
    gitdeploy.update_supervisorctl()
    flash("Command updated.")
    return redirect(url_for("www.dashboard"))
