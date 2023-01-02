from flask import session, url_for, redirect, request, render_template, flash

from app import ag, sec
from .. import bp


@bp.route('/login', methods=["GET", "POST"])
@sec.no_login_required('www.dashboard', 'logged_in')
def login():
    settings = ag.read_settings()
    if settings["FIRST_RUN"]:
        return redirect(url_for("www.first_run"))

    if request.method == "POST":
        t1 = request.form.get("t1")
        t2 = request.form.get("t2")

        if t1 == settings.get("T1") and t2 == settings.get("T2"):
            session["logged_in"] = True
            session.modified = True
            return redirect(url_for("www.dashboard"))
        else:
            flash("Invalid tokens")
            return render_template(bp.tmpl("login.html"))

    return render_template(bp.tmpl("login.html"), staging=True)
