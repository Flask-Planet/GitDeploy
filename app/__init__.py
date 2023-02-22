from time import sleep

from flask import Flask

from app.extensions import bigapp, gitdeploy

gitdeploy.init_supervisorctl()
gitdeploy.set_tokens()

while True:
    sleep(1)
    if gitdeploy.status_supervisorctl():
        gitdeploy.update_supervisorctl()
        break


def create_app():
    app = Flask(__name__)
    bigapp.init_app(app)
    bigapp.import_blueprint("www")
    bigapp.import_blueprint("api")
    bigapp.import_theme("theme")

    return app


wsgi = create_app()
