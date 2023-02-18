from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/manual-destroy-venv')
@security.login_required('www.login', 'logged_in')
def manual_destroy_venv():
    gitdeploy.read_conf()
    response = {"success": True, "alerts": []}

    gitdeploy.stop_satellite()
    gitdeploy.destroy_venv()

    response["alerts"].append("Venv destroyed.")
    return response
