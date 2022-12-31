from app import ag
from .. import bp


@bp.route('/webhook/<string:secret>', methods=['POST', 'GET'])
def webhook(secret):
    settings = ag.read_settings()
    settings_secret = settings.get('WH_SECRET')

    if settings_secret is None or settings_secret != secret:
        return 'unauthorised', 403

    ag.repo_pull()
    ag.repo_install_requirements()
    ag.restart_satellite()
    return 'pulled', 200
