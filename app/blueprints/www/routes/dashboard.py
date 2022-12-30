import os

from flask import render_template

from app import ag, sec
from .. import bp


@bp.get('/dashboard')
@sec.login_required('www.login', 'logged_in')
def dashboard():
    settings = ag.read_settings()
    repo_folder = os.listdir(ag.repo_dir)
    return render_template(
        bp.tmpl("dashboard.html"),
        settings=settings,
        status=ag.status_satellite(),
        repo_folder=repo_folder
    )
