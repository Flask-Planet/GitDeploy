from pathlib import Path

from app import ag
from .. import bp


@bp.route('/webhook/<string:secret>', methods=['POST', 'GET'])
def webhook(secret):
    settings = ag.read_settings()
    settings_secret = settings.get('WH_SECRET')

    if settings_secret is None or settings_secret != secret:
        return 'unauthorised', 403

    if settings["GIT"]:
        if Path(ag.repo_dir / ".git").exists():
            ag.repo_pull()
            ag.repo_install_requirements()
            ag.restart_satellite()
            return 'pulled', 200

    return 'Repo not configured', 500
