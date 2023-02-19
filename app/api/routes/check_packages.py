from app.extensions import security, gitdeploy, terminator
from .. import bp


def remove_spaces(s):
    if s == "":
        return False
    if s == " ":
        return False
    if s is None:
        return False
    return s


@bp.get('/check-packages')
@security.login_required('www.login', 'logged_in')
def check_packages():
    if gitdeploy.env.repo_python.exists():
        with terminator(
                "venv/bin/pip", working_directory=gitdeploy.repo_dir
        ) as command:
            out, err = command("freeze")
            packages = list(filter(remove_spaces, out.split("\n")))
            return {"packages": list(packages)}
    else:
        return {"packages": []}
