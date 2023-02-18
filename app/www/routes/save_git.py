from flask import url_for, redirect, request, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.post('/save/git')
@security.login_required('www.login', 'logged_in')
def save_git():
    gitdeploy.read_conf()

    git_url = request.form.get("git_url")
    git_private = request.form.get("git_private", "off")
    git_token_name = request.form.get("git_token_name")
    git_token = request.form.get("git_token")

    if "https://" not in git_url:
        flash("Git URL must start with https://")
        return redirect(url_for("www.dashboard"))

    gitdeploy.set_conf("GIT_URL", git_url, write=True)

    if git_private == "on":

        if not git_token_name:
            flash("Git has been set to require an access token, but no token name was provided.")
            return redirect(url_for("www.dashboard"))

        if not git_token:
            flash("Git has been set to require an access token, but no token was provided.")
            return redirect(url_for("www.dashboard"))

        gitdeploy.set_conf("GIT_PRIVATE", True)
        gitdeploy.set_conf("GIT_TOKEN_NAME", git_token_name)
        gitdeploy.set_conf("GIT_TOKEN", git_token)

        gitdeploy.write_conf()
        if gitdeploy.repo_dot_git_config.exists():
            if not gitdeploy.set_dot_git_config_with_token():
                flash("Git settings have been saved, but the .git/config file could not be updated.")
                return redirect(url_for("www.dashboard"))

    else:

        gitdeploy.set_conf("GIT_PRIVATE", False)
        gitdeploy.set_conf("GIT_TOKEN_NAME", None)
        gitdeploy.set_conf("GIT_TOKEN", None)

        gitdeploy.write_conf()
        if gitdeploy.repo_dot_git_config.exists():
            if not gitdeploy.set_dot_git_config_without_token():
                flash("Git settings have been saved, but the .git/config file could not be updated.")
                return redirect(url_for("www.dashboard"))

    flash("Git settings have been saved.")
    return redirect(url_for("www.dashboard"))
