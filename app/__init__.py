from flask import Flask

from app.extensions import bigapp, background_tasks


def create_app():
    app = Flask(__name__)
    bigapp.init_app(app)
    bigapp.import_blueprint("www")
    bigapp.import_blueprint("api")
    bigapp.import_theme("theme")

    background_tasks.start()

    return app
