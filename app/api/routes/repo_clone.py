from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/clone-repo')
@security.login_required('www.login', 'logged_in')
def repo_clone():
    gitdeploy.read_conf()
    response = {"success": False, "alerts": []}

    if gitdeploy.conf.get("GIT_URL"):

        if gitdeploy.repo_dot_git_config.exists():
            response["alerts"].append("Git repository already exists. Destroy it first.")
            return response

        for line in gitdeploy.clone_repo():
            if "private" in line:
                response["alerts"].append("This git repository is private. Please enter your credentials.")
                gitdeploy.destroy_repo()
                return response

        response["success"] = True
        response["alerts"].append("Git repository cloned.")
        return response

    else:

        response["alerts"].append("Git is not configured.")
        return response
