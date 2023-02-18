from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/clone-repo')
@security.login_required('www.login', 'logged_in')
def clone_repo():
    gitdeploy.read_conf()
    response = {"success": False, "alerts": []}

    if gitdeploy.conf.get("GIT"):
        if gitdeploy.repo_dot_git_config.exists():
            response["alerts"].append("Git repository already exists. Destroy it first.")
            return response

        gitdeploy.clone_repo()
        response["success"] = True
        response["alerts"].append("Git repository cloned successfully.")
        return response

    else:
        response["alerts"].append("Git is not configured.")
        return response
