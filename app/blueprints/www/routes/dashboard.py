import os

from flask import render_template

from app import ag, sec
from .. import bp


@bp.get('/dashboard')
@sec.login_required('www.login', 'logged_in')
def dashboard():
    settings = ag.read_settings()
    repo_folder = os.listdir(ag.repo_dir)
    resp_app = ag.supervisorctl_status("satellite", True)

    if "RUNNING" in resp_app:
        app_running = True
    else:
        app_running = False

    return render_template(
        bp.tmpl("dashboard.html"),
        settings=settings,
        status=app_running,
        repo_folder=repo_folder
    )
