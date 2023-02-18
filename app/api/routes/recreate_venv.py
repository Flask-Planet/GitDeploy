from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/recreate-venv')
@security.login_required('www.login', 'logged_in')
def recreate_venv():
    gitdeploy.read_conf()
    response = {"success": True, "alerts": []}

    gitdeploy.stop_satellite()
    gitdeploy.destroy_venv()
    gitdeploy.create_venv()

    response["alerts"].append("Venv recreated.")
    return response
