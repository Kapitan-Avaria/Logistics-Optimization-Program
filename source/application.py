from flask import Flask


def create_application():

    app = Flask(__name__)
    # app.config.from_pyfile('config.py')

    return app
