import json

from flask import request, redirect, url_for

from app import ag, sec
from .. import bp


def pull_repo():
    ag.stop_satellite()
    ag.repo_pull()
    ag.repo_install_requirements()
    ag.start_satellite()


@bp.post('/webhook/<string:secret>')
def webhook(secret):
    settings = ag.read_settings()
    enabled = settings.get('WH_ENABLED', False)
    settings_secret = settings.get('WH_SECRET')

    if not enabled:
        return 'webhook disabled', 500

    if settings_secret is None or settings_secret != secret:
        return 'unauthorised', 403

    if not enabled:
        return 'webhook disabled', 500

    if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        if request.headers.get("X-GitHub-Event") == "push":
            payload = request.form.get("payload")
            data = json.loads(payload)

            try:
                ref = data.get("ref").split("/")[-1]
            except IndexError:
                ref = "null"

            if ref == "main":
                hook_git = data.get("repository").get("clone_url")
                if hook_git == settings.get("GIT_URL"):
                    pull_repo()
                    return "pulled", 200

            else:

                return "not main branch", 200

    if request.headers.get("Content-Type") == "application/json":
        payload = request.json

        try:
            ref = payload.get("ref").split("/")[-1]
        except IndexError:
            ref = "null"

        if ref == "main":
            hook_git = payload.get("repository").get("clone_url")
            if hook_git == settings.get("GIT_URL"):
                pull_repo()
                return "pulled", 200

            else:

                return "not main branch", 200

    return f'Incorrect content type', 500


@bp.get('/webhook/status')
def webhook_status():
    settings = ag.read_settings()
    enabled = settings.get('WH_ENABLED', False)

    if not enabled:
        return 'webhook disabled', 500

    return 'webhook enabled', 200


@bp.get('/enable-webhook')
@sec.login_required('www.login', 'logged_in')
def enable_webhook():
    settings = ag.read_settings()
    settings["WH_ENABLED"] = True
    ag.write_settings(settings)
    return redirect(url_for("www.dashboard"))


@bp.get('/disable-webhook')
@sec.login_required('www.login', 'logged_in')
def disable_webhook():
    settings = ag.read_settings()
    settings["WH_ENABLED"] = False
    ag.write_settings(settings)
    return redirect(url_for("www.dashboard"))
