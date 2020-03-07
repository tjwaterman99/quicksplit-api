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
        assert exposure.scope == user.admin_token.scope
        assert exposure == experiment.last_exposure_production
        assert exposure == cohort.last_exposure_production
        assert exposure == subject.last_exposure_production
        assert experiment.subjects_counter_production == 1
        assert experiment.subjects_counter_staging == 0
        assert exposure.created_at == experiment.last_exposure_at
        assert exposure.created_at == cohort.last_exposure_at
        assert exposure.created_at == subject.last_exposure_at

        exposure_duplicate = Exposure.create(
            subject_name=subject.name,
            cohort_name=cohort.name,
            experiment_name=experiment.name
        )
        assert exposure_duplicate.scope == user.admin_token.scope
        assert exposure_duplicate.id == exposure.id
        assert exposure_duplicate == experiment.last_exposure_production
        assert exposure_duplicate == cohort.last_exposure_production
        assert exposure_duplicate == subject.last_exposure_production
        # We can't test the subjects_counter logic here, since it requires
        # the results of an `on conflict` statement which won't get pulled
        # accurately from inside this single test transaction.
        # assert experiment.subjects_counter_production == 1
        # assert experiment.subjects_counter_staging == 0
        assert exposure_duplicate.last_seen_at == experiment.last_exposure_at
        assert exposure_duplicate.last_seen_at == cohort.last_exposure_at
        assert exposure_duplicate.last_seen_at == subject.last_exposure_at


def test_exposure_create_staging(db, app, user, experiment, cohort, subject_staging):
    subject = subject_staging
    with app.test_request_context(headers={'Authorization': user.admin_token_staging.value}):
        app.preprocess_request()
        exposure = Exposure.create(
            subject_name=subject.name,
            cohort_name=cohort.name,
            experiment_name=experiment.name
        )
        assert exposure.scope == user.admin_token_staging.scope
        assert exposure == experiment.last_exposure_staging
        assert exposure == cohort.last_exposure_staging
        assert exposure == subject.last_exposure_staging
        assert None == experiment.last_exposure_production
        assert None == cohort.last_exposure_production
        assert None == subject.last_exposure_production
        assert experiment.subjects_counter_production == 0
        assert experiment.subjects_counter_staging == 1
        assert exposure.created_at == experiment.last_exposure_at
        assert exposure.created_at == cohort.last_exposure_at
        assert exposure.created_at == subject.last_exposure_at

        exposure_duplicate = Exposure.create(
            subject_name=subject.name,
            cohort_name=cohort.name,
            experiment_name=experiment.name
        )
        assert exposure_duplicate.scope == user.admin_token_staging.scope
        assert exposure_duplicate.id == exposure.id
        assert exposure_duplicate == experiment.last_exposure_staging
        assert exposure_duplicate == cohort.last_exposure_staging
        assert exposure_duplicate == subject.last_exposure_staging
        assert None == experiment.last_exposure_production
        assert None == cohort.last_exposure_production
        assert None == subject.last_exposure_production
        # We can't test the subjects_counter logic here, since it requires
        # the results of an `on conflict` statement which won't get pulled
        # accurately from inside this single test transaction.
        # assert experiment.subjects_counter_production == 0
        # assert experiment.subjects_counter_staging == 1
        assert exposure_duplicate.last_seen_at == experiment.last_exposure_at
        assert exposure_duplicate.last_seen_at == cohort.last_exposure_at
        assert exposure_duplicate.last_seen_at == subject.last_exposure_at

        # Note that we can't test this from inside a single transaction.
        # assert exposure_duplicate.last_seen_at != exposure_duplicate.created_at


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
        assert conversion.scope == user.admin_token.scope
        assert conversion.value == 20
        assert conversion == experiment.last_conversion_production
        assert conversion == conversion.exposure.cohort.last_conversion_production
        assert conversion == subject.last_conversion_production
        assert conversion.created_at == experiment.last_conversion_at
        assert conversion.created_at == conversion.exposure.cohort.last_conversion_at
        assert conversion.created_at == subject.last_conversion_at

        conversion_duplicate = Conversion.create(
            subject_name=subject.name,
            experiment_name=experiment.name,
            value=30
        )
        assert conversion_duplicate.scope == user.admin_token.scope
        assert conversion_duplicate.value == 20  # don't update original value
        assert conversion_duplicate == experiment.last_conversion_production
        assert conversion_duplicate == conversion.exposure.cohort.last_conversion_production
        assert conversion_duplicate == subject.last_conversion_production
        assert conversion_duplicate.last_seen_at == experiment.last_conversion_at
        assert conversion_duplicate.last_seen_at == conversion.exposure.cohort.last_conversion_at
        assert conversion_duplicate.last_seen_at == subject.last_conversion_at


def test_conversion_create_staging(db, app, user, experiment, subject_staging, exposure_staging):
    subject = subject_staging
    exposure = exposure_staging

    with app.test_request_context(headers={'Authorization': user.admin_token_staging.value}):
        app.preprocess_request()
        conversion = Conversion.create(
            subject_name=subject.name,
            experiment_name=experiment.name,
            value=20
        )
        assert conversion.scope == user.admin_token_staging.scope
        assert conversion.value == 20
        assert conversion == experiment.last_conversion_staging
        assert conversion == conversion.exposure.cohort.last_conversion_staging
        assert conversion == subject.last_conversion_staging
        assert conversion.created_at == experiment.last_conversion_at
        assert conversion.created_at == conversion.exposure.cohort.last_conversion_at
        assert conversion.created_at == subject.last_conversion_at

        conversion_duplicate = Conversion.create(
            subject_name=subject.name,
            experiment_name=experiment.name,
            value=30
        )
        assert conversion_duplicate.scope == user.admin_token_staging.scope
        assert conversion_duplicate.value == 20  # don't update original value
        assert conversion_duplicate == experiment.last_conversion_staging
        assert conversion_duplicate == conversion.exposure.cohort.last_conversion_staging
        assert conversion_duplicate == subject.last_conversion_staging
        assert conversion_duplicate.last_seen_at == experiment.last_conversion_at
        assert conversion_duplicate.last_seen_at == conversion.exposure.cohort.last_conversion_at
        assert conversion_duplicate.last_seen_at == subject.last_conversion_at


def test_free_plan_has_no_schedule(user):
    assert user.account.plan.schedule == None
