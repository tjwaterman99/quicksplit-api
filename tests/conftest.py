import random
import os
import uuid
import datetime as dt

import pytest
import sqlalchemy

from app import create_app
from app.models import db as _db, Role, Plan, Account, User, Subject, Experiment, Exposure, Conversion, Token, Cohort
from app.seeds import plans, roles


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
        _db.session.add_all(plans)
        _db.session.add_all(roles)
        _db.session.commit()
        yield _db
        _db.drop_all()


@pytest.fixture()
def email():
    return f"tester+{random.random()}@gmail.com"


@pytest.fixture()
def db(database):
    database.session.begin_nested()
    yield database
    database.session.rollback()
    database.session.remove()


@pytest.fixture()
def user(db, email):
    plan = Plan.query.filter(Plan.name=="free").first()
    role = Role.query.filter(Role.name=="admin").first()
    token = Token(role=role, value=uuid.uuid4())
    account = Account.create(plan=plan)
    user = User.create(email=email, password="password", token=token, account=account)
    db.session.add(user)
    db.session.add(token)
    db.session.add(account)
    db.session.flush()
    return user


@pytest.fixture()
def experiment(db, user):
    experiment = Experiment(user=user, name="Test Experiment", active=True, last_activated_at=dt.datetime.now())
    db.session.add(experiment)
    db.session.flush()
    return experiment


@pytest.fixture()
def subject(db, user):
    subject = Subject(account=user.account, name='test-subject-1')
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
def exposure(db, subject, experiment, cohort):
    exposure = Exposure(subject=subject, experiment=experiment, cohort=cohort)
    experiment.subjects_counter += 1
    db.session.add(exposure)
    db.session.add(experiment)
    db.session.flush()
    return exposure


@pytest.fixture()
def conversion(db, exposure):
    conversion = Conversion(exposure=exposure, value=30.0)
    db.session.add(conversion)
    db.session.flush()
    return conversion


@pytest.fixture()
def client(db, app, user):
    client = app.test_client()
    client.environ_base['HTTP_AUTHORIZATION'] = f"{user.tokens[0].value}"
    return client
