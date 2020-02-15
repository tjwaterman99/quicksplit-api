import os
import pytest
import sqlalchemy

from app import create_app
from app.models import db as _db, Account, User


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
    database.session.rollback()
    database.session.begin(subtransactions=True)
    yield database
    database.session.rollback()


@pytest.fixture()
def client(db, app):
    return app.test_client()


@pytest.fixture()
def account(db):
    account = Account()
    db.session.add(account)
    db.session.commit()
    return account


@pytest.fixture()
def user(db, account):
    user = User(account=account)
    db.session.add(user)
    db.session.commit()
    return user
