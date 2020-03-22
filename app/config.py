import os


class ProductionConfig(object):
    SECRET_KEY = os.environ['SECRET_KEY']
    DATABASE_URL = os.environ['DATABASE_URL']
    REDIS_URL = os.environ['REDIS_URL']
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    PROPAGATE_EXCEPTIONS = True
    STRIPE_TEST_PUBLISHABLE_KEY = os.environ['STRIPE_TEST_PUBLISHABLE_KEY']
    STRIPE_TEST_SECRET_KEY = os.environ['STRIPE_TEST_SECRET_KEY']
    STRIPE_PRODUCTION_PUBLISHABLE_KEY = os.environ['STRIPE_PRODUCTION_PUBLISHABLE_KEY']
    STRIPE_PRODUCTION_SECRET_KEY = os.environ['STRIPE_PRODUCTION_SECRET_KEY']
    WORKER_QUEUES = ['default']


class TestingConfig(ProductionConfig):
    TESTING = True
    DATABASE_URL = os.environ['DATABASE_URL'].replace('/quicksplit-dev', '/quicksplit-testing')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(ProductionConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
