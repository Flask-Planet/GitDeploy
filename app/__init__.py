import os

from flask import Flask, session
from flask_bigapp import BigApp, Security

from autogit import AutoGit
from autogit.tools import Tools

ba = BigApp()
sec = Security()

ag = AutoGit()

ag.setup()
ag.auto_deploy()

settings = ag.read_settings()

if settings["AUTOGIT_SK"]:
    os.environ["AUTOGIT_SK"] = settings["AUTOGIT_SK"]
else:
    settings["AUTOGIT_SK"] = Tools.generate_random_token(128)
    os.environ["AUTOGIT_SK"] = settings["AUTOGIT_SK"]
    ag.write_settings(settings)

os.environ["AUTOGIT_ENV"] = "True"


def create_app():
    app = Flask(__name__)
    ba.init_app(app)
    ba.import_blueprints("blueprints")
    ba.import_theme("theme")

    return app
