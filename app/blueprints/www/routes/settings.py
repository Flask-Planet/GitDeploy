from flask import url_for, redirect, request, render_template

from app import ag, sec
from .. import bp


@bp.route('/settings', methods=["GET", "POST"])
@sec.login_required('www.login', 'logged_in')
def settings_app():
    settings = ag.read_settings()

    if request.method == "POST":
        settings["GIT"] = request.form.get("git")
        settings["COMMAND"] = request.form.get("command")
        settings["WH_SECRET"] = request.form.get("wh_secret")

        if request.form.get("auto_deploy") == "on":
            ag.write_settings(settings, auto_actions=True)
        else:
            ag.write_settings(settings, auto_actions=False)

        return redirect(url_for("www.dashboard"))

    return render_template(bp.tmpl("settings.html"), settings=settings)
