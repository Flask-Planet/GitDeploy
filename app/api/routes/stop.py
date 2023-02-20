from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/stop')
@security.login_required('www.login', 'logged_in')
def stop_app():
    response = {"success": False, "alerts": []}
    response['alerts'].append(
        gitdeploy.stop_satellite()
    )
    response['success'] = True
    return response
