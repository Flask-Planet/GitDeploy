from flask import url_for, redirect, render_template, request, session

from app.extensions import gitdeploy
from .. import bp


@bp.route('/first-run', methods=["GET", "POST"])
def first_run():
    gitdeploy.read_conf()

    if not gitdeploy.conf.get("FIRST_RUN"):
        return redirect(url_for("www.login"))

    if request.method == "POST":
        session["logged_in"] = True
        gitdeploy.set_conf("FIRST_RUN", False, write=True)
        return redirect(url_for("www.dashboard"))

    return render_template(
        bp.tmpl("first_run.html"),
        staging=True,
        t1=gitdeploy.conf.get("T1"),
        t2=gitdeploy.conf.get("T2")
    )
