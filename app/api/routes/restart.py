from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/restart')
@security.login_required('www.login', 'logged_in')
def restart_app():
    gitdeploy.read_conf()
    response = {"success": False, "alerts": []}

    if not gitdeploy.conf.get('COMMAND'):
        response['alerts'].append('No command set to start the app.')
        return response
    response['alerts'].append(
        gitdeploy.restart_satellite()
    )
    response['success'] = True
    return response
