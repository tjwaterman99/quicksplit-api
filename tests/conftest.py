import random
import os
import uuid
import datetime as dt

import pytest
import sqlalchemy

from app import create_app
from app.models import (
    db as _db, Role, Plan, Account, User, Subject, Experiment, Exposure,
    Conversion, Token, Cohort, Scope
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


@pytest.fixture()
def email():
    return f"tester@gmail.com"


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
def user(db, email, production_scope):
    return User.create(email=email, password="password")


@pytest.fixture()
def free_plan(db):
    return Plan.query.filter(Plan.price_in_cents==0).first()


@pytest.fixture()
def paid_plan(db):
    return Plan.query.filter(Plan.price_in_cents > 0).first()


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
    exposure = Exposure(subject=subject_staging, experiment=experiment, cohort=cohort, scope=staging_scope)
    experiment.subjects_counter_staging += 1
    db.session.add(exposure)
    db.session.add(experiment)
    db.session.flush()
    return exposure


@pytest.fixture()
def conversion(db, exposure, production_scope):
    conversion = Conversion(exposure=exposure, value=30.0, scope=production_scope)
    db.session.add(conversion)
    db.session.flush()
    return conversion


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
