import os

from flask import Flask
from flask_migrate import Migrate
from werkzeug.utils import import_string

from app.views import root
from app.models import db, Account, User, Experiment, Subject, Exposure, Conversion


def shell_context():
    return {
        'db': db,
        'Account': Account,
        'User': User,
        'Experiment': Experiment,
        'Subject': Subject,
        'Exposure': Exposure,
        'Conversion': Conversion
    }


def create_app():
    env_string = os.environ['FLASK_ENV'].capitalize()
    config = import_string(f'app.config.{env_string}Config')

    app = Flask(__name__)
    app.config.from_object(config)

    migrate = Migrate(db)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(root)
    app.shell_context_processor(shell_context)

    return app
