import os


class ProductionConfig(object):
    DATABASE_URL = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(ProductionConfig):
    DATABASE_URL = os.environ['DATABASE_URL'].replace('/development', '/testing')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(ProductionConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
