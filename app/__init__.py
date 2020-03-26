import os
import datetime
from uuid import UUID

import stripe
from flask import (
    Flask, current_app, json, make_response, request, g, jsonify, session
)
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import import_string

from app.resources import api
from app.models import (
    db, Account, User, Token, Experiment, Subject, Exposure, Conversion,
    Cohort, Scope, PlanSchedule, Order, Session
)
from app.services import ExperimentResultCalculator
from app.exceptions import (
    ApiException, handle_api_exception, handle_uncaught_exception,
    handle_route_not_found_exception
)
from app.commands import seed, rollup, worker
from app.encoders import CustomJSONEncoder
from app.proxies import get_worker, get_mailer, get_redis


def load_session():
    sess = Session.query.get(session['id'])
    if not sess:
        raise ApiException(403, "Invalid session id")
    else:
        g.user = sess.user

        # Pull environment from request body or query params
        if request.json and 'environment' in request.json:
            environment = request.json.pop('environment')
        elif 'environment' in request.args:  # ie query params
            environment = request.args['environment']
        else:
            environment = 'production'

        # Set token based on environment value
        if environment == "staging":
            g.token = g.user.admin_token_staging
        elif environment == "production":
            g.token = g.user.admin_token
        else:
            raise ApiException(403, f"Invalid environment: {environment}")


def load_token():
    token_value = request.headers['Authorization']
    try:
        UUID(token_value)
    except ValueError:
        raise ApiException(403, "Invalid token: not uuid")
    token = Token.query.filter(Token.value==token_value).first()
    if not token:
        raise ApiException(403, "Invalid token")
    else:
        g.token = token
        g.user = token.user


def load_user():
    if 'session' in request.cookies:
        load_session()
    elif 'Authorization' in request.headers:
        load_token()
    else:
        g.user = None
        g.token = None


def parse_json():
    request.get_json(force=True, silent=True, cache=True)


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
        'user': User.query.order_by(User.created_at.asc()).first(),
        'stripe': stripe,
        'mailer': get_mailer(),
        'worker': get_worker(),
        'redis': get_redis()
    }


def create_app():
    env_string = os.environ['FLASK_ENV'].capitalize()
    config = import_string(f'app.config.{env_string}Config')

    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, resources={
        '/conversions': {'origins': '*'},
        '/exposures': {'origins': '*'},
        # TODO: once the new www is deployed, only allow origin 'www.quicksplit.io',
        '*': {'origins': '*', 'supports_credentials': True}
    })

    migrate = Migrate(db)
    app.json_encoder = CustomJSONEncoder

    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    app.shell_context_processor(shell_context)
    app.before_request(parse_json)
    app.before_request(load_user)

    app.register_error_handler(Exception, handle_uncaught_exception)
    app.register_error_handler(ApiException, handle_api_exception)
    app.register_error_handler(404, handle_route_not_found_exception)

    app.cli.add_command(seed)
    app.cli.add_command(rollup)
    app.cli.add_command(worker)

    return app
