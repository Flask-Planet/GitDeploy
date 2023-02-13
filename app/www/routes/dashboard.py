import os

from flask import render_template, request, redirect, url_for, flash

from app.extensions import security, gitdeploy, terminator
from .. import bp


@bp.route('/dashboard', methods=['GET', 'POST'])
@security.login_required('www.login', 'logged_in')
def dashboard():
    if request.method == 'POST':
        install = request.form.get('install')
        if install:
            with terminator(f"venv/bin/pip install", working_directory=gitdeploy.repo_dir) as command:
                out, err = command(install)
                flash(out, "success")
                return redirect(url_for("www.dashboard"))

    if gitdeploy.repo_python.exists():
        venv = True
    else:
        venv = False

    gitdeploy.read_conf()
    repo_folder = os.listdir(gitdeploy.repo_dir)

    if gitdeploy.repo_git_config.exists():
        git_exists = True
    else:
        git_exists = False

    with terminator("supervisord") as command:
        out, err = command("satellite status")
        if "RUNNING" in out:
            app_running = True
        else:
            app_running = False

    return render_template(
        bp.tmpl("dashboard.html"),
        settings=gitdeploy.conf,
        status=app_running,
        repo_folder=repo_folder,
        venv=venv,
        git_exists=git_exists,
    )
