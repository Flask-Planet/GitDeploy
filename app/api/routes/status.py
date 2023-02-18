from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/status')
@security.login_required('www.login', 'logged_in')
def status():
    response = {
        "repo_contents": gitdeploy.get_repo_contents(),
        "satellite_status": gitdeploy.status_satellite(),
        "venv_exists": gitdeploy.repo_venv_bin.exists(),
    }
    return response
