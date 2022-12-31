import os

from flask import Flask
from flask_bigapp import BigApp, Security

from .autogit import AutoGitExtension, Tools

ba = BigApp()
sec = Security()
ag = AutoGitExtension()

ag.setup()
ag.auto_deploy()

os.environ["AUTOGIT_SK"] = Tools.generate_random_token(256)

ag.del_autogit_log()


def create_app():
    app = Flask(__name__)
    ba.init_app(app)
    ba.import_blueprints("blueprints")
    ba.import_structures("structures")

    return app
