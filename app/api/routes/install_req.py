from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/install-requirements')
@security.login_required('www.login', 'logged_in')
def install_req():
    gitdeploy.read_conf()
    response = {"success": False, "alerts": []}

    if gitdeploy.env.repo_pip.exists():
        if not gitdeploy.env.repo_requirements_file.exists():
            response["alerts"].append(
                "requirements.txt was not found in repo, add this file to the root of your repo and pull.")
            return response

        gitdeploy.install_requirements()
        response["success"] = True
        response["alerts"].append("Requirements installed.")
        return response

    response["alerts"].append("pip is not installed.")
    return response
