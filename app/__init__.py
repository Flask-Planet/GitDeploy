from flask import Flask

from app.extensions import bigapp, gitdeploy

gitdeploy.init_supervisorctl()


def create_app():
    app = Flask(__name__)
    bigapp.init_app(app)
    bigapp.import_blueprint("www")
    bigapp.import_blueprint("api")
    bigapp.import_theme("theme")

    return app
