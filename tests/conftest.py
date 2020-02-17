import random
import os
import uuid

import pytest
import sqlalchemy

from app import create_app
from app.models import db as _db, Account, User, Subject, Experiment, Exposure, Conversion, Token


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


@pytest.fixture(scope="session")
def database(app):
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture()
def db(database):
    database.session.begin_nested()
    yield database
    database.session.rollback()
    database.session.close()


@pytest.fixture()
def account(db):
    account = Account()
    db.session.add(account)
    return account


@pytest.fixture()
def token(db):
    return Token(id=uuid.uuid4())


@pytest.fixture()
def email():
    return f"tester+{random.random()}@gmail.com"


@pytest.fixture()
def user(db, account, token, email):
    db.session.add(token)
    user = User.create(account=account, email=email, password="password", token=token)
    db.session.add(user)
    return user


@pytest.fixture()
def experiment(db, user):
    experiment = Experiment(user=user, name="Test Experiment")
    db.session.add(experiment)
    return experiment


@pytest.fixture()
def subject(db, experiment):
    subject = Subject(user=experiment.user, id='test-subject-1')
    db.session.add(subject)
    return subject


@pytest.fixture()
def exposure(db, subject, experiment,  user):
    exposure = Exposure(subject=subject, experiment=experiment, user=user)
    db.session.add(exposure)
    return exposure


@pytest.fixture()
def conversion(db, subject, experiment,  user):
    conversion = Conversion(subject=subject, experiment=experiment, user=user)
    db.session.add(conversion)
    return conversion


@pytest.fixture()
def client(db, app, user):
    client = app.test_client()
    client.environ_base['HTTP_AUTHORIZATION'] = f"{user.token.id}"
    return client
