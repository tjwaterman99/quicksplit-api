import os

from flask import Flask
from flask_migrate import Migrate
from werkzeug.utils import import_string

from app.resources import api, load_user
from app.models import db, close_db_session, Account, User, Experiment, Subject, Exposure, Conversion


def shell_context():
    return {
        'db': db,
        'Account': Account,
        'User': User,
        'Experiment': Experiment,
        'Subject': Subject,
        'Exposure': Exposure,
        'Conversion': Conversion,
        'user': User.query.first()
    }


def create_app():
    env_string = os.environ['FLASK_ENV'].capitalize()
    config = import_string(f'app.config.{env_string}Config')

    app = Flask(__name__)
    app.config.from_object(config)

    migrate = Migrate(db)

    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    app.shell_context_processor(shell_context)
    app.before_request(load_user)
    app.teardown_appcontext(close_db_session)

    return app
