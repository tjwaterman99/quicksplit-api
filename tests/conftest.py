import random
import os
import uuid
import datetime as dt

import pytest
import sqlalchemy

from app import create_app
from app.models import (
    db as _db, Role, Plan, Account, User, Subject, Experiment, Exposure,
    Conversion, Token, Cohort, Scope, PlanSchedule, ExposureRollup, ExperimentResult
)
from app.seeds import plans, roles, scopes, plan_schedules


os.environ.setdefault('QUICKSPLIT_API_URL', 'http://web:5000')


@pytest.fixture(scope='session')
def dbconn():
    engine = sqlalchemy.engine.create_engine(os.environ['DATABASE_URL'])
    conn = engine.connect()
    conn.execution_options(isolation_level="AUTOCOMMIT").execute('drop database if exists testing;')
    conn.execution_options(isolation_level="AUTOCOMMIT").execute('create database testing;')
    return dbconn


@pytest.fixture(scope='session')
def app(dbconn):
    os.environ['FLASK_ENV'] = 'testing'
    return create_app()


@pytest.fixture(scope='session')
def database(app):
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        _db.session.add_all(plan_schedules)
        _db.session.add_all(plans)
        _db.session.add_all(roles)
        _db.session.add_all(scopes)
        _db.session.commit()
        yield _db
        _db.drop_all()


@pytest.fixture(scope='session')
def stripe_customer_id():
    return Account.create_stripe_customer(stripe_livemode=False)['id']


@pytest.fixture()
def email():
    return f"tester@quicksplit.io"


@pytest.fixture()
def password():
    return "password"


@pytest.fixture()
def db(database):
    database.session.begin_nested()
    yield database
    database.session.rollback()
    database.session.remove()


@pytest.fixture()
def production_scope():
    return Scope.query.filter(Scope.name=='production').first()


@pytest.fixture()
def staging_scope():
    return Scope.query.filter(Scope.name=='staging').first()


@pytest.fixture()
def account(db, stripe_customer_id):
    account = Account.create(stripe_customer_id=stripe_customer_id)
    return account


@pytest.fixture()
def user(db, email, account, production_scope, password):
    return User.create(email=email, password=password, account=account)


@pytest.fixture()
def free_plan(db):
    return Plan.query.filter(Plan.price_in_cents==0).first()


@pytest.fixture()
def paid_plan(db):
    return Plan.query.filter(Plan.price_in_cents > 0).first()


@pytest.fixture()
def monthly_schedule(db):
    return PlanSchedule.query.filter(PlanSchedule.name=="monthly").first()


@pytest.fixture()
def annual_schedule(db):
    return PlanSchedule.query.filter(PlanSchedule.name=="annual").first()


@pytest.fixture()
def monthly_developer_plan(db,  monthly_schedule):
    return Plan.query.filter(Plan.name=="developer")\
                     .filter(Plan.schedule_id==monthly_schedule.id)\
                     .first()


@pytest.fixture()
def annual_developer_plan(db,  annual_schedule):
    return Plan.query.filter(Plan.name=="developer")\
                     .filter(Plan.schedule_id==annual_schedule.id)\
                     .first()


@pytest.fixture()
def experiment(db, user):
    experiment = Experiment(user=user, name="Test Experiment", active=True, last_activated_at=dt.datetime.now())
    db.session.add(experiment)
    db.session.flush()
    return experiment


@pytest.fixture()
def subject(db, user, production_scope):
    subject = Subject(account=user.account, name='test-subject-1', scope=production_scope)
    db.session.add(subject)
    db.session.flush()
    return subject


@pytest.fixture()
def subject_staging(db, user, staging_scope):
    subject = Subject(account=user.account, name='test-subject-1', scope=staging_scope)
    db.session.add(subject)
    db.session.flush()
    return subject


@pytest.fixture()
def cohort(db, experiment):
    cohort = Cohort(name='experimental', experiment=experiment)
    db.session.add(cohort)
    db.session.flush()
    return cohort


@pytest.fixture()
def exposure(db, subject, experiment, cohort, production_scope):
    exposure = Exposure(subject=subject, experiment=experiment, cohort=cohort, scope=production_scope)
    experiment.subjects_counter_production += 1
    db.session.add(exposure)
    db.session.add(experiment)
    db.session.flush()
    return exposure


@pytest.fixture()
def exposure_staging(db, subject_staging, experiment, cohort, staging_scope):
    exposure = Exposure(subject=subject_staging, experiment=experiment, cohort=cohort, scope=staging_scope, last_seen_at=dt.datetime.now())
    experiment.subjects_counter_staging += 1
    db.session.add(exposure)
    db.session.add(experiment)
    db.session.flush()
    return exposure


@pytest.fixture()
def conversion(db, exposure, production_scope):
    conversion = Conversion(exposure=exposure, value=30.0, scope=production_scope, last_seen_at=dt.datetime.now())
    db.session.add(conversion)
    db.session.flush()
    return conversion


@pytest.fixture()
def exposures_rollup(db, exposure):
    rollup = ExposureRollup(
        day=exposure.last_seen_at.date(),
        user_id=exposure.experiment.user_id,
        account_id=exposure.experiment.user.account_id,
        experiment_id=exposure.experiment.id,
        experiment_name=exposure.experiment.name,
        scope_id=exposure.scope.id,
        exposures=1,
        conversions=0
    )
    db.session.add(rollup)
    db.session.flush()
    return rollup


@pytest.fixture()
def experiment_result(db, user, experiment, production_scope, exposure, conversion):
    experiment_result = ExperimentResult(scope=production_scope, experiment=experiment, user=user)
    db.session.add(experiment_result)
    db.session.flush()
    return experiment_result


@pytest.fixture()
def logged_out_client(db, app):
    return app.test_client()


@pytest.fixture()
def client(db, app, user):
    client = app.test_client()
    production_token = list(filter(lambda t: t.scope.name=="production", user.tokens))[0]
    client.environ_base['HTTP_AUTHORIZATION'] = f"{str(production_token.value)}"
    return client


@pytest.fixture()
def admin_staging_client(db, app, user):
    client = app.test_client()
    token = list(filter(lambda t: t.scope.name=="staging" and t.role.name=="admin", user.tokens))[0]
    client.environ_base['HTTP_AUTHORIZATION'] = f"{str(token.value)}"
    return client


@pytest.fixture()
def public_staging_client(db, app, user):
    client = app.test_client()
    token = list(filter(lambda t: t.scope.name=="staging" and t.role.name=="public", user.tokens))[0]
    client.environ_base['HTTP_AUTHORIZATION'] = f"{str(token.value)}"
    return client


@pytest.fixture()
def public_production_client(db, app, user):
    client = app.test_client()
    token = list(filter(lambda t: t.scope.name=="production" and t.role.name=="public", user.tokens))[0]
    client.environ_base['HTTP_AUTHORIZATION'] = f"{str(token.value)}"
    return client
