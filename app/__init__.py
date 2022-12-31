import os
from pathlib import Path

from flask import Flask
from flask_bigapp import BigApp, Security

from .autogit import AutoGitExtension, Tools

ba = BigApp()
sec = Security()
_this_path = Path().cwd()
ag = AutoGitExtension(_this_path, allow_supervisor=False)

ag.setup()
ag.auto_deploy()

os.environ["AUTOGIT_SK"] = Tools.generate_random_token(256)
os.environ["AUTOGIT_ENV"] = "True"

ag.del_autogit_log()


def create_app():
    app = Flask(__name__)
    ba.init_app(app)
    ba.import_blueprints("blueprints")
    ba.import_structures("structures")

    return app
