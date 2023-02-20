import json

from flask import request

from app.extensions import security, gitdeploy
from .. import bp


def pull_repo():
    gitdeploy.stop_satellite()
    gitdeploy.update_repo()
    gitdeploy.install_requirements()
    gitdeploy.start_satellite()


@bp.post('/webhook/<string:secret>')
def webhook(secret):
    gitdeploy.read_conf()
    enabled = gitdeploy.conf.get('WH_ENABLED', False)
    webhook_secret = gitdeploy.conf.get('WH_SECRET')
    default_branch = gitdeploy.conf.get('GIT_BRANCH', 'master')

    if not enabled:
        return 'webhook disabled', 500

    if webhook_secret is None or webhook_secret != secret:
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

            if ref == default_branch:
                hook_git = data.get("repository").get("clone_url")
                if hook_git == gitdeploy.conf.get("GIT_URL"):
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

        if ref == default_branch:
            hook_git = payload.get("repository").get("clone_url")
            if hook_git == gitdeploy.conf.get("GIT_URL"):
                pull_repo()
                return "pulled", 200

            else:

                return "not main branch", 200

    return f'Incorrect content type', 500


@bp.get('/webhook/status')
def webhook_status():
    gitdeploy.read_conf()
    enabled = gitdeploy.conf.get('WH_ENABLED', False)

    if not enabled:
        return 'webhook disabled', 500

    return 'webhook enabled', 200


@bp.get('/enable-webhook')
@security.login_required('www.login', 'logged_in')
def enable_webhook():
    response = {"success": True, "alerts": ['Webhook enabled']}
    gitdeploy.set_conf("WH_ENABLED", True, write=True)
    return response


@bp.get('/disable-webhook')
@security.login_required('www.login', 'logged_in')
def disable_webhook():
    response = {"success": True, "alerts": ['Webhook disabled']}
    gitdeploy.set_conf("WH_ENABLED", False, write=True)
    return response
