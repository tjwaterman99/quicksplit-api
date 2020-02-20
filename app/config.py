import os


class ProductionConfig(object):
    DATABASE_URL = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    PRESERVE_CONTEXT_ON_EXCEPTION = True


class TestingConfig(ProductionConfig):
    DATABASE_URL = os.environ['DATABASE_URL'].replace('/development', '/testing')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(ProductionConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
