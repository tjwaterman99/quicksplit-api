import sqlalchemy


def test_env_string(app):
    assert app.config['ENV'] == 'testing'


def test_db_string(app):
    conn_string = sqlalchemy.engine.url.make_url(app.config['DATABASE_URL'])
    assert conn_string.database == 'quicksplit-testing'


def test_db_conn(app):
    eng = sqlalchemy.engine.create_engine(app.config['DATABASE_URL'])
    assert eng.table_names() is not None
