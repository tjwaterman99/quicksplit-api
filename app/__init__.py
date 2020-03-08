import os
import datetime

from flask import Flask, current_app, json, make_response, request, g
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import import_string

from app.resources import api
from app.models import (
    db, Account, User, Token, Experiment, Subject, Exposure, Conversion,
    Cohort, Scope, PlanSchedule, Order
)
from app.services import ExperimentResultCalculator
from app.exceptions import ApiException
from app.commands import seed


class CustomJSONEncoder(json.JSONEncoder):
  "Add support for serializing timedeltas"

  def default(self, o):
    if type(o) == datetime.timedelta:
      return str(o)
    elif type(o) == datetime.datetime:
      return o.isoformat()
    else:
      return super().default(o)


def handle_api_exception(exc):
    if not current_app.testing:
        db.session.rollback()
    return make_response(json.dumps(exc), exc.status_code)


def handle_uncaught_exception(exc):
    if not current_app.testing:
        db.session.rollback()
    current_app.logger.error("Unhandled error: " + str(exc))
    resp = {
        'data': None,
        'message': "Unexpected exception occured. Please try again later.",
        'status_code': 500
    }
    return make_response(json.dumps(resp), 500)


def load_user():
    token_value = request.headers.get('Authorization')
    if not token_value:
        g.user = None
        g.token = None
        return

    # Note that public routes will reject a user with an invalid token. That
    # seems a bit counter-intuitive, since those routes shouldn't be validating
    # the token.
    token = Token.query.filter(Token.value==token_value).first()
    if not token:
        raise ApiException(403, "Permission denied. Invalid token.")

    g.user = token.user
    g.token = token


def shell_context():
    return {
        'db': db,
        'Account': Account,
        'User': User,
        'Experiment': Experiment,
        'Subject': Subject,
        'Exposure': Exposure,
        'Conversion': Conversion,
        'Cohort': Cohort,
        'Scope': Scope,
        'Token': Token,
        'ExperimentResultCalculator': ExperimentResultCalculator,
        'PlanSchedule': PlanSchedule,
        'user': User.query.order_by(User.created_at.desc()).first()
    }


def create_app():
    env_string = os.environ['FLASK_ENV'].capitalize()
    config = import_string(f'app.config.{env_string}Config')

    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, resources={
        '/conversions': {'origins': '*'},
        '/exposures': {'origins': '*'},
        '/*': {
            'origins': [
                'http://127.0.0.1:8080',
                'https://www.quicksplit.io',
                'https://*.netlify.com'
             ]
        }
    })

    migrate = Migrate(db)

    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    app.shell_context_processor(shell_context)
    app.before_request(load_user)

    app.register_error_handler(Exception, handle_uncaught_exception)
    app.register_error_handler(ApiException, handle_api_exception)

    app.cli.add_command(seed)

    app.json_encoder = CustomJSONEncoder

    return app
