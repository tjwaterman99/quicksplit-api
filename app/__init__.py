import traceback
import os
import datetime
from uuid import UUID

os.environ.setdefault('PORT', '5000')
os.environ.setdefault('SECRET_KEY', 'notsecret')
os.environ.setdefault('FLASK_APP', 'app')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('PYTHONPATH', '/')
os.environ.setdefault('DATABASE_URL', 'postgresql://quicksplit:notsecret@127.0.0.1:5432/quicksplit-dev')
os.environ.setdefault('REDIS_URL', 'redis://127.0.0.1:6379/0')
os.environ.setdefault('QUICKSPLIT_API_URL', 'http://127.0.0.1:5000')
os.environ.setdefault('HEROKU_RELEASE_CREATED_AT', str(datetime.datetime.now()))
os.environ.setdefault('HEROKU_RELEASE_VERSION', 'development')
os.environ.setdefault('HEROKU_SLUG_COMMIT', 'development')

# These are all "test" keys in development, but we include all
# versions in production so that test-users get sent to the test-stripe
# data, even if they're created on the production app
os.environ.setdefault('STRIPE_TEST_PUBLISHABLE_KEY', 'pk_test_vs6w4emCv9szUa8mJyeXKTey00IV5800C2')
os.environ.setdefault('STRIPE_TEST_SECRET_KEY', 'sk_test_InjhthRyfgYjrOXULoSylt4g009H6voKLf')
os.environ.setdefault('STRIPE_PRODUCTION_PUBLISHABLE_KEY', 'pk_test_vs6w4emCv9szUa8mJyeXKTey00IV5800C2')
os.environ.setdefault('STRIPE_PRODUCTION_SECRET_KEY', 'sk_test_InjhthRyfgYjrOXULoSylt4g009H6voKLf')

# Sendgrid api key that can send demo emails
os.environ.setdefault('SENDGRID_API_KEY', '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')

from flask import (
    Flask, current_app, json, make_response, request, g, jsonify, session
)
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import import_string
import stripe

from app.resources import api
from app.models import (
    db, Account, User, Token, Experiment, Subject, Exposure, Conversion,
    Cohort, Scope, PlanSchedule, Order, Session
)
from app.services import ExperimentResultCalculator
from app.exceptions import ApiException
from app.commands import seed, rollup, worker
from app.encoders import CustomJSONEncoder
from app.proxies import get_worker, get_mailer, get_redis


def handle_api_exception(exc):
    if not current_app.testing:
        db.session.rollback()
    return make_response(json.dumps(exc), exc.status_code)


def handle_uncaught_exception(exc):
    if not current_app.testing:
        db.session.rollback()
    current_app.logger.error("Unhandled error: " + str(exc))
    current_app.logger.error(traceback.format_exc())
    resp = {
        'data': None,
        'message': "Unexpected exception occured. Please try again later.",
        'status_code': 500
    }
    return make_response(json.dumps(resp), 500)


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

    app.cli.add_command(seed)
    app.cli.add_command(rollup)
    app.cli.add_command(worker)

    return app
