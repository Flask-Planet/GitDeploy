from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/get-repo-contents')
@security.login_required('www.login', 'logged_in')
def get_repo_contents():
    return {"repo_contents": gitdeploy.get_repo_contents()}
