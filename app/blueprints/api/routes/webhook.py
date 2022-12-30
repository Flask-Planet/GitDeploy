from app import ag
from .. import bp


@bp.get('/webhook/<string:secret>')
def webhook(secret):
    settings = ag.read_settings()
    settings_secret = settings.get('WH_SECRET')

    if settings_secret is None or settings_secret != secret:
        return 'unauthorised', 403

    ag.repo_pull()
    ag.restart_satellite()
    return 'pulled', 200
