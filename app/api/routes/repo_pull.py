from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/pull-repo')
@security.login_required('www.login', 'logged_in')
def repo_pull():
    gitdeploy.read_conf()
    response = {"success": False, "alerts": []}

    if gitdeploy.conf.get("GIT"):

        if not gitdeploy.env.repo_dot_git_config.exists():
            response["alerts"].append("Git repository does not exist. Clone it first.")
            return response

        for line in gitdeploy.update_repo():
            if "Already up-to-date" in line:
                response["alerts"].append("No changes to pull.")
                return response

        gitdeploy.install_requirements()
        gitdeploy.restart_satellite()
        response["alerts"].append("Changes pulled.")
        return response

    else:
        response["alerts"].append("Git is not configured.")
        return response
