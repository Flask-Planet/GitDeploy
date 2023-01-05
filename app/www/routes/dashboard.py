import os

from flask import render_template, request, redirect, url_for, flash

from app import ag, sec
from autogit.pip_cli import PipCli
from .. import bp


@bp.route('/dashboard', methods=['GET', 'POST'])
@sec.login_required('www.login', 'logged_in')
def dashboard():
    if request.method == 'POST':
        install = request.form.get('install')
        if install:
            with PipCli(f"install {install}", ag.repo_dir) as output:
                flash(output)
                return redirect(url_for("www.dashboard"))

    if ag.repo_python_instance.exists():
        venv = True
    else:
        venv = False

    settings = ag.read_settings()
    repo_folder = os.listdir(ag.repo_dir)
    resp_app = ag.supervisorctl_status("satellite", True)

    if ag.repo_git_config.exists():
        git_exists = True
    else:
        git_exists = False

    if "RUNNING" in resp_app:
        app_running = True
    else:
        app_running = False

    return render_template(
        bp.tmpl("dashboard.html"),
        settings=settings,
        status=app_running,
        repo_folder=repo_folder,
        venv=venv,
        git_exists=git_exists,
    )
