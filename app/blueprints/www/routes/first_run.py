from flask import url_for, redirect, render_template, request, session

from app import ag
from .. import bp


@bp.route('/first-run', methods=["GET", "POST"])
def first_run():
    if request.method == "POST":
        session["logged_in"] = True
        session.modified = True
        return redirect(url_for("www.dashboard"))

    settings = ag.read_settings()
    session["logged_in"] = False
    session.modified = True
    if not settings["FIRST_RUN"]:
        return redirect(url_for("www.login"))

    new_tokens = ag.set_tokens(settings)

    return render_template(
        bp.tmpl("first_run.html"),
        staging=True,
        t1=new_tokens.get("T1"),
        t2=new_tokens.get("T2")
    )
