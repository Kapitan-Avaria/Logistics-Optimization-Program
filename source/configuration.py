from flask import Flask
import os
import json


def configure_application(application: Flask) -> None:
    base_path = os.path.abspath(".")
    file_path = os.path.join(base_path, 'data/config.cfg')
    application.config.from_file(file_path, load=json.load)
