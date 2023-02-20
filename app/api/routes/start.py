from app.extensions import security, gitdeploy
from .. import bp


@bp.get('/start')
@security.login_required('www.login', 'logged_in')
def start_app():
    gitdeploy.read_conf()
    response = {"success": False, "alerts": []}

    if not gitdeploy.conf.get('COMMAND'):
        response['alerts'].append('No command set to start the app.')
        return response

    response['alerts'].append(
        gitdeploy.start_satellite()
    )
    response['success'] = True
    return response
