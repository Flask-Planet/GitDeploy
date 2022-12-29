import os
import secrets

from flask import Flask, redirect, url_for, session, render_template, request, flash
from flask_bigapp import Security

from utils import AppController, Gitter, read_settings, write_settings, init_settings, wash_command, generate_random_token

AG_PORT = os.getenv("AG_PORT", 5500)
AG_HOST = os.getenv("AG_HOST", "0.0.0.0")

gitter = Gitter()
sec = Security()


def create_app(satellite_app):
    git_app = Flask(__name__)
    git_app.secret_key = secrets.token_urlsafe(16)
    init_settings()

    @git_app.before_request
    def before_request():
        if "logged_in" not in session:
            session["logged_in"] = False

    @git_app.get('/')
    def index():
        if not read_settings()["T1"]:
            return redirect(url_for("first_run"))

        if session.get("logged_in"):
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("login"))

    @git_app.get('/first-run')
    def first_run():
        settings = read_settings()
        if settings["T1"] is not None:
            return redirect(url_for("login"))

        t1 = generate_random_token(24)
        t2 = generate_random_token(24)
        t3 = generate_random_token(24)

        settings["T1"] = t1
        settings["T2"] = t2
        settings["T3"] = t3

        write_settings(settings)

        return render_template("first_run.html", t1=t1, t2=t2, t3=t3)

    @git_app.route('/login', methods=["GET", "POST"])
    @sec.no_login_required('dashboard', 'logged_in')
    def login():
        settings = read_settings()
        if settings["T1"] is None:
            return redirect(url_for("first_run"))

        if request.method == "POST":
            settings = read_settings()

            setting_tokens = [settings["T1"], settings["T2"], settings["T3"]]
            form_tokens = [request.form.get("t1"), request.form.get("t2"), request.form.get("t3")]

            if setting_tokens == form_tokens:
                session["logged_in"] = True
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid tokens")
                return render_template("login.html")

        return render_template("login.html")

    @git_app.get('/logout')
    def logout():
        session.pop("logged_in", None)
        return redirect(url_for("login"))

    @git_app.get('/dashboard')
    @sec.login_required('login', 'logged_in')
    def dashboard():
        settings = read_settings()
        repo_folder = os.listdir(gitter.REPO_FOLDER)
        return render_template(
            "dashboard.html",
            settings=settings,
            status=satellite_app.status(),
            repo_folder=repo_folder
        )

    @git_app.get('/webhook/<string:secret>')
    def webhook(secret):
        settings = read_settings()
        settings_secret = settings.get('WH_SECRET')

        if settings_secret is None or settings_secret != secret:
            return 'unauthorised', 403

        satellite_app.stop()
        gitter.pull()
        satellite_app.start()
        return 'pulled', 200

    @git_app.get('/manual-pull')
    @sec.login_required('login', 'logged_in')
    def manual_pull():
        settings = read_settings()
        if settings["GIT"]:
            if os.listdir(gitter.REPO_FOLDER):
                gitter.pull()
                return redirect(url_for("dashboard"))
            else:
                gitter.setup(settings["GIT"])
                gitter.install_requirements()
                return redirect(url_for("dashboard"))
        else:
            flash("Git is not configured")
            return redirect(url_for("dashboard"))

    @git_app.get('/start')
    @sec.login_required('login', 'logged_in')
    def start_app():
        command = read_settings().get('COMMAND')
        if command is None:
            flash("No command set")
            return redirect(url_for("dashboard"))
        else:
            if not satellite_app.start(wash_command(command)):
                flash("There was an error starting the app")
                return redirect(url_for("dashboard"))
        return redirect(url_for("dashboard"))

    @git_app.get('/stop')
    @sec.login_required('login', 'logged_in')
    def stop_app():
        if satellite_app.stop():
            return redirect(url_for("dashboard"))
        flash("No command set")
        return redirect(url_for("dashboard"))

    @git_app.route('/settings', methods=["GET", "POST"])
    @sec.login_required('login', 'logged_in')
    def settings_app():
        settings = read_settings()

        if request.method == "POST":
            if request.form.get("git") == "None":
                git = None
            else:
                git = request.form.get("git")

            if request.form.get("command") == "None":
                command = None
            else:
                command = request.form.get("command")

            if request.form.get("wh_secret") == "None":
                wh_secret = None
            else:
                wh_secret = request.form.get("wh_secret")

            if git != settings.get("GIT"):
                settings["GIT"] = git
                if os.listdir(gitter.REPO_FOLDER):
                    gitter.destroy()

            if command != settings.get("COMMAND"):
                settings["COMMAND"] = command
                satellite_app.stop()

            if wh_secret != settings.get("WH_SECRET"):
                settings["WH_SECRET"] = wh_secret

            write_settings(settings)
            return redirect(url_for("dashboard"))

        return render_template("settings.html", settings=settings)

    return git_app


if __name__ == "__main__":
    with AppController(create_app) as app:
        app.run(port=AG_PORT, host=AG_HOST)
