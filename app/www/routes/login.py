from flask import session, url_for, redirect, request, render_template, flash

from app.extensions import security, gitdeploy
from .. import bp


@bp.route('/login', methods=["GET", "POST"])
@security.no_login_required('www.dashboard', 'logged_in', show_message=False)
def login():
    gitdeploy.read_conf()
    if gitdeploy.conf.get("FIRST_RUN"):
        return redirect(url_for("www.first_run"))

    if request.method == "POST":
        t1 = request.form.get("t1")
        t2 = request.form.get("t2")

        if t1 == gitdeploy.conf.get("T1") and t2 == gitdeploy.conf.get("T2"):
            session["logged_in"] = True
            return redirect(url_for("www.dashboard"))
        else:
            flash("Invalid tokens")
            return render_template(bp.tmpl("login.html"))

    return render_template(bp.tmpl("login.html"), staging=True)
