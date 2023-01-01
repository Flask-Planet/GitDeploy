from pathlib import Path

from app import ag
from .. import bp


@bp.route('/webhook/<string:secret>', methods=['POST'])
def webhook(secret):
    settings = ag.read_settings()
    settings_secret = settings.get('WH_SECRET')

    if settings_secret is None or settings_secret != secret:
        return 'unauthorised', 403

    if settings["GIT"]:
        if Path(ag.repo_dir / ".git").exists():
            ag.stop_satellite()
            ag.repo_pull()
            ag.repo_install_requirements()
            ag.start_satellite()
            return 'pulled', 200

    return 'Repo not configured', 500
