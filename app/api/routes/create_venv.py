from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/create-venv')
@security.login_required('www.login', 'logged_in')
def create_venv():
    gitdeploy.read_conf()
    response = {"success": False, "alerts": []}

    if not gitdeploy.repo_python.exists():
        gitdeploy.create_venv()
        response["success"] = True
        response["alerts"].append("Venv created.")
        return response

    response["alerts"].append("Venv already exists.")
    return response
