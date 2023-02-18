from pathlib import Path

from flask import url_for, redirect, request, render_template, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.route('/settings', methods=["GET", "POST"])
@security.login_required('www.login', 'logged_in')
def settings_app():
    gitdeploy.read_conf()

    if request.method == "POST":
        gitdeploy.set_conf("GIT_URL", request.form.get("git_url"))

        if request.form.get("git_private", "off") == "on":
            if not request.form.get("git_username"):
                flash("Git token name is required")
                return redirect(url_for("www.settings_app"))

            if not request.form.get("git_password"):
                flash("Git token password is required")
                return redirect(url_for("www.settings_app"))

            gitdeploy.set_conf("GIT_PRIVATE", True)
            gitdeploy.set_conf("GIT_TOKEN_NAME", request.form.get("git_token_name"))
            gitdeploy.set_conf("GIT_TOKEN", request.form.get("git_token"))

        else:

            gitdeploy.set_conf("GIT_PRIVATE", False)
            gitdeploy.set_conf("GIT_TOKEN_NAME", None)
            gitdeploy.set_conf("GIT_TOKEN", None)

        gitdeploy.set_conf("COMMAND", request.form.get("command"))
        gitdeploy.set_conf("WH_SECRET", request.form.get("wh_secret"))

        gitdeploy.write_conf()

        return redirect(url_for("www.dashboard"))

    if gitdeploy.repo_dot_git_file.exists():
        repo_exists = True
    else:
        repo_exists = False

    return render_template(bp.tmpl("settings.html"), settings=gitdeploy.conf, repo_exists=repo_exists)
