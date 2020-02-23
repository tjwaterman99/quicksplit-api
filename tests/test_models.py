import pytest

from app.models import Account, User, Experiment, Subject, Exposure, Conversion, Token, Role
from app.exceptions import ApiException


def test_user_create(db, production_scope):
    user = User.create(email="tester@gmail.com",  password="password")
    assert User.query.first() == user
    assert Account.query.first() == user.account
    assert user.check_password('password')
    assert user.has_role('admin')
    with pytest.raises(ApiException) as exc:
        User.create(email="tester@gmail.com", password="password")
        assert "User with that email already exists." in exc.message


def test_user_has_role(user):
    assert user.has_role('admin')


def test_experiment_init(user, db):
    experiment = Experiment(user=user, name="Test experiment")
    experiment.activate()
    assert experiment.user == user
    assert experiment in user.experiments.all()
    assert experiment.active == True


def test_experiment_create(app, user, db):
    with app.test_request_context(headers={'Authorization': user.admin_token.value}):
        app.preprocess_request()
        experiment = Experiment.create(name="test experiment")
        assert experiment.user == user
        assert experiment.name == "test experiment"


def test_experiment_acivate_deactivate(user, db, experiment):
    assert experiment.active == True
    experiment.deactivate()
    assert experiment.active == False
    experiment.activate()
    assert experiment.active == True


def test_subject_init(db, user, production_scope):
    subject = Subject(name='test-subject-1', account=user.account, scope=production_scope)
    db.session.add(subject)
    db.session.flush()
    assert user in Subject.query.get(subject.id).account.users.all()
    assert subject in user.account.subjects.all()


def test_exposure_init(db, experiment, cohort, subject, production_scope):
    exposure = Exposure(experiment=experiment, cohort=cohort, subject=subject, scope=production_scope)
    db.session.add(exposure)
    db.session.flush()
    assert exposure in subject.exposures.all()
    assert exposure in cohort.exposures.all()
    assert exposure in experiment.exposures.all()


def test_exposure_create(db, app, user, experiment, cohort, subject):
    with app.test_request_context(headers={'Authorization': user.admin_token.value}):
        app.preprocess_request()
        exposure = Exposure.create(
            subject_name=subject.name,
            cohort_name=cohort.name,
            experiment_name=experiment.name
        )
        assert exposure


def test_conversion_init(db, exposure, production_scope):
    conversion = Conversion(exposure=exposure, scope=production_scope)
    db.session.add(conversion)
    db.session.flush()
    assert conversion == exposure.conversion


def test_conversion_create(db, app, user, experiment, subject, exposure):
    with app.test_request_context(headers={'Authorization': user.admin_token.value}):
        app.preprocess_request()
        conversion = Conversion.create(
            subject_name=subject.name,
            experiment_name=experiment.name,
            value=20
        )
        assert conversion
