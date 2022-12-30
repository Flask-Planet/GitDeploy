from flask import url_for, redirect, render_template, request, session

from app import ag
from .. import bp


@bp.route('/first-run', methods=["GET", "POST"])
def first_run():
    settings = ag.read_settings()

    if request.method == "POST":
        settings["FIRST_RUN"] = False
        ag.write_settings(settings)
        session["logged_in"] = True
        return redirect(url_for("www.dashboard"))

    if not settings["FIRST_RUN"]:
        return redirect(url_for("www.login"))

    return render_template(
        bp.tmpl("first_run.html"),
        t1=settings.get("T1"),
        t2=settings.get("T2")
    )
