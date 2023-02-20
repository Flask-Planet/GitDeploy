import os

from flask import render_template

from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/dashboard')
@security.login_required('www.login', 'logged_in')
def dashboard():
    gitdeploy.read_conf()

    repo_folder = os.listdir(gitdeploy.env.repo_dir)
    command_exists = False
    venv_exists = False
    repo_dot_git_config_exists = False

    settings = {
        "GIT_URL": gitdeploy.conf.get("GIT_URL"),
        "GIT_PRIVATE": gitdeploy.conf.get("GIT_PRIVATE"),
        "GIT_TOKEN_NAME": gitdeploy.conf.get("GIT_TOKEN_NAME"),
        "GIT_TOKEN": gitdeploy.conf.get("GIT_TOKEN"),
        "COMMAND": gitdeploy.conf.get("COMMAND"),
        "WH_ENABLED": gitdeploy.conf.get("WH_ENABLED"),
        "WH_SECRET": gitdeploy.conf.get("WH_SECRET"),
    }

    if gitdeploy.env.repo_dot_git_config.exists():
        repo_dot_git_config_exists = True

    if gitdeploy.env.repo_venv_bin.exists():
        if gitdeploy.conf.get("COMMAND"):
            if gitdeploy.conf.get("COMMAND") in os.listdir(gitdeploy.env.repo_venv_bin):
                command_exists = True

    if gitdeploy.env.repo_python.exists():
        venv_exists = True

    return render_template(
        bp.tmpl("dashboard.html"),
        settings=settings,
        repo_folder=repo_folder,
        venv_exists=venv_exists,
        repo_dot_git_config_exists=repo_dot_git_config_exists,
        git_url_exists=True if gitdeploy.conf.get("GIT") else False,
        command_exists=command_exists,
    )
