import pytest

from app.models import Account, User, Experiment, Subject, Exposure, Conversion, Token, Role


def test_user_create(db, production_scope):
    account = Account.create()
    user = User.create(account=account, email="tester@gmail.com",  password="password")
    assert User.query.first() == user
    assert Account.query.first() == account
    assert user in account.users.all()
    assert account == user.account
    assert user.check_password('password')


def test_user_has_role(user):
    assert user.has_role('admin')


def test_experiment_create(user, db):
    experiment = Experiment(user=user, name="Test experiment")
    experiment.activate()
    assert experiment.user == user
    assert experiment in user.experiments.all()
    assert experiment.active == True


def test_experiment_acivate_deactivate(user, db, experiment):
    assert experiment.active == True
    experiment.deactivate()
    assert experiment.active == False
    experiment.activate()
    assert experiment.active == True


def test_subject_create(db, user, production_scope):
    subject = Subject(name='test-subject-1', account=user.account, scope=production_scope)
    db.session.add(subject)
    db.session.flush()
    assert user in Subject.query.get(subject.id).account.users.all()
    assert subject in user.account.subjects.all()


def test_exposure_create(db, experiment, cohort, subject, production_scope):
    exposure = Exposure(experiment=experiment, cohort=cohort, subject=subject, scope=production_scope)
    db.session.add(exposure)
    db.session.flush()
    assert exposure in subject.exposures.all()
    assert exposure in cohort.exposures.all()
    assert exposure in experiment.exposures.all()


def test_conversion_create(db, exposure, production_scope):
    conversion = Conversion(exposure=exposure, scope=production_scope)
    db.session.add(conversion)
    db.session.flush()
    assert conversion == exposure.conversion
