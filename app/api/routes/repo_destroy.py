from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/destroy-repo')
@security.login_required('www.login', 'logged_in')
def repo_destroy():
    gitdeploy.stop_satellite()
    gitdeploy.destroy_repo()
    return {"success": True, "alerts": ["Git repository destroyed successfully"]}
