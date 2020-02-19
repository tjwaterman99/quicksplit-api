import pytest

from app.models import Account, User, Experiment, Subject, Exposure, Conversion, Token, Role


def test_user_create(db):
    role = Role.query.filter(Role.name=="admin").first()
    token = Token(role=role)
    account = Account.create()
    user = User.create(account=account, token=token, email="tester@gmail.com",  password="password")
    db.session.add(user)
    db.session.commit()
    assert User.query.first() == user
    assert Account.query.first() == account
    assert user in account.users.all()
    assert account == user.account
    assert token in user.tokens
    assert user.check_password('password')


def test_experiment_create(user, db):
    experiment = Experiment(user=user, name="Test experiment")
    experiment.activate()
    db.session.add(experiment)
    db.session.commit()
    assert experiment.user == user
    assert experiment in user.experiments.all()
    assert experiment.active == True


def test_experiment_acivate_deactivate(user, db, experiment):
    db.session.add(experiment)
    db.session.commit()
    assert experiment.active == True
    experiment.deactivate()
    assert experiment.active == False
    experiment.activate()
    assert experiment.active == True


def test_subject_create(user, db):
    subject = Subject(name='test-subject-1', account=user.account)
    db.session.add(subject)
    db.session.commit()
    assert user in Subject.query.get(subject.id).account.users.all()
    assert subject in user.account.subjects.all()


def test_exposure_create(db, experiment, cohort, subject):
    exposure = Exposure(experiment=experiment, cohort=cohort, subject=subject)
    db.session.add(exposure)
    db.session.commit()
    assert exposure in subject.exposures.all()
    assert exposure in cohort.exposures.all()
    assert exposure in experiment.exposures.all()


def test_conversion_create(db, exposure):
    conversion = Conversion(exposure=exposure)
    db.session.add(conversion)
    db.session.commit()
    assert conversion == exposure.conversion
