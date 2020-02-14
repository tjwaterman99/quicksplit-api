import os

from flask import Flask
from werkzeug.utils import import_string

from app.views import root
from app.models import db


def create_app():
    env_string = os.environ['FLASK_ENV'].capitalize()
    config = import_string(f'app.config.{env_string}Config')

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    app.register_blueprint(root)


    return app
