import os

from flask import render_template, request, redirect, url_for, flash

from app.extensions import security, gitdeploy, terminator
from .. import bp


@bp.route('/dashboard', methods=['GET'])
@security.login_required('www.login', 'logged_in')
def dashboard():
    gitdeploy.read_conf()

    repo_folder = os.listdir(gitdeploy.repo_dir)
    command_exists = False
    venv_exists = False
    repo_dot_git_config_exists = False

    settings = {
        "GIT": gitdeploy.conf.get("GIT"),
        "GIT_PRIVATE": gitdeploy.conf.get("GIT_PRIVATE"),
        "GIT_TOKEN_NAME": gitdeploy.conf.get("GIT_TOKEN_NAME"),
        "GIT_TOKEN": gitdeploy.conf.get("GIT_TOKEN"),
        "COMMAND": gitdeploy.conf.get("COMMAND"),
    }

    if gitdeploy.repo_dot_git_config.exists():
        repo_dot_git_config_exists = True

    if gitdeploy.repo_venv_bin.exists():
        if gitdeploy.conf("COMMAND"):
            if gitdeploy.conf("COMMAND") in os.listdir(gitdeploy.repo_venv_bin):
                command_exists = True

    if gitdeploy.repo_python.exists():
        venv_exists = True

    if request.method == 'POST':
        install = request.form.get('install')
        if install:
            with terminator(f"venv/bin/pip install", working_directory=gitdeploy.repo_dir) as command:
                out, err = command(install)
                flash(out, "success")
                return redirect(url_for("www.dashboard"))

    with terminator("supervisord") as command:
        out, err = command("satellite status")
        if "RUNNING" in out:
            app_running = True
        else:
            app_running = False

    return render_template(
        bp.tmpl("dashboard.html"),
        settings=settings,
        status=app_running,
        repo_folder=repo_folder,
        venv_exists=venv_exists,
        repo_dot_git_config_exists=repo_dot_git_config_exists,
        git_url_exists=gitdeploy.conf.get("GIT"),
        command_exists=command_exists,
    )
