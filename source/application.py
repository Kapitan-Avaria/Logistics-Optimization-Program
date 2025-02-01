from flask import Flask
from source.web.blueprint import create_app_blueprint


def create_application():

    app = Flask(__name__)
    # app.config.from_pyfile('config.py')
    app.register_blueprint(create_app_blueprint())

    return app
