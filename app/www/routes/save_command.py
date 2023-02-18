from flask import url_for, redirect, request, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.post('/save/command')
@security.login_required('www.login', 'logged_in')
def save_command():
    for key, value in request.form.items():
        print(f'{key}: {value}')

    gitdeploy.read_conf()
    gitdeploy.set_conf('COMMAND', request.form.get("command", None), write=True)
    gitdeploy.write_satellite_ini()
    flash("Command updated.")
    return redirect(url_for("www.dashboard"))
