from pathlib import Path

from flask import url_for, redirect, request, render_template, flash

from app import ag, sec
from .. import bp


@bp.route('/settings', methods=["GET", "POST"])
@sec.login_required('www.login', 'logged_in')
def settings_app():
    settings = ag.read_settings()

    if request.method == "POST":
        settings["GIT_URL"] = request.form.get("git_url")

        if request.form.get("git_private", "off") == "on":
            if not request.form.get("git_username"):
                flash("Git token name is required")
                return redirect(url_for("www.settings_app"))

            if not request.form.get("git_password"):
                flash("Git token password is required")
                return redirect(url_for("www.settings_app"))

            settings["GIT_PRIVATE"] = True
            settings["GIT_USERNAME"] = request.form.get("git_username")
            settings["GIT_PASSWORD"] = request.form.get("git_password")
        else:
            settings["GIT_PRIVATE"] = False
            settings["GIT_USERNAME"] = None
            settings["GIT_PASSWORD"] = None

        settings["COMMAND"] = request.form.get("command")
        settings["WH_SECRET"] = request.form.get("wh_secret")

        if request.form.get("auto_deploy") == "on":
            ag.write_settings(settings, auto_actions=True)
        else:
            ag.write_settings(settings, auto_actions=False)

        return redirect(url_for("www.dashboard"))

    if Path(ag.repo_dir / ".git").exists():
        repo_exists = True
    else:
        repo_exists = False

    return render_template(bp.tmpl("settings.html"), settings=settings, repo_exists=repo_exists)
