from flask import url_for, redirect, render_template, request, session

from app.extensions import gitdeploy
from .. import bp


@bp.route('/first-run', methods=["GET", "POST"])
def first_run():
    if request.method == "POST":
        session["logged_in"] = True
        session.modified = True
        return redirect(url_for("www.dashboard"))

    gitdeploy.read_conf()
    session["logged_in"] = False
    session.modified = True
    if not gitdeploy.conf.get("FIRST_RUN"):
        return redirect(url_for("www.login"))

    gitdeploy.set_tokens()

    return render_template(
        bp.tmpl("first_run.html"),
        staging=True,
        t1=gitdeploy.conf.get("T1"),
        t2=gitdeploy.conf.get("T2")
    )
