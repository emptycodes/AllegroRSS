from flask import Flask
from app.allegro import allegro_api


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.settings.{0}".format(app.env))

    app.register_blueprint(allegro_api)

    return app
