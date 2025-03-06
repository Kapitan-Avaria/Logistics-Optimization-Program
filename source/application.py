from flask import Flask
from source.web.blueprint import create_app_blueprint
from configuration import configure_application


def create_application():

    app = Flask(__name__)
    configure_application(app)
    app.register_blueprint(create_app_blueprint())

    return app
