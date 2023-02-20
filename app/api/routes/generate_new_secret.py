from app.extensions import security, gitdeploy, Tools
from .. import bp


@bp.get('/generate-new-secret')
@security.login_required('www.login', 'logged_in')
def generate_new_secret():
    response = {"success": True, "alerts": ['New secret generated.']}
    gitdeploy.read_conf()
    gitdeploy.set_conf("WH_SECRET", Tools.generate_random_token(64), write=True)
    return response
