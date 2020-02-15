from app.models import Account, User, Experiment, Subject, Exposure, Conversion


def test_user_create(db):
    account = Account()
    user = User(account=account)
    db.session.add(user)
    db.session.commit()
    assert User.query.first() == user
    assert Account.query.first() == account
    assert user in account.users.all()
    assert account == user.account


def test_user_delete(user, experiment, db):
    db.session.delete(user)
    db.session.commit()
    assert User.query.get(user.id) == None


def test_experiment_create(user, db):
    experiment = Experiment(user=user, name="Test experiment")
    db.session.add(experiment)
    db.session.commit()
    assert experiment.user == user
    assert experiment in user.experiments.all()


def test_experiment_delete(experiment, db):
    db.session.delete(experiment)
    db.session.commit()
    assert Experiment.query.get(experiment.id) is None


def test_subject_create(user, db):
    subject = Subject(user=user, id='test-subject-1')
    db.session.add(subject)
    db.session.commit()
    assert Subject.query.get([subject.id, user.id]).user == user
    assert subject in user.subjects.all()


def test_subject_delete(user, subject, db):
    db.session.delete(subject)
    db.session.commit()
    assert Subject.query.get([subject.id, user.id]) == None
    assert subject not in user.subjects.all()


def test_exposure_create(db, subject, experiment,  user):
    exposure = Exposure(subject=subject, experiment=experiment, user=user)
    db.session.add(exposure)
    db.session.commit()
    assert exposure in subject.exposures.all()
    assert exposure in user.exposures.all()
    assert exposure in experiment.exposures.all()


def test_exposure_delete(db, exposure, user, experiment, subject):
    db.session.delete(exposure)
    db.session.commit()
    assert exposure not in subject.exposures.all()
    assert exposure not in user.exposures.all()
    assert exposure not in experiment.exposures.all()


def test_conversion_create(db, subject, experiment,  user):
    conversion = Conversion(subject=subject, experiment=experiment, user=user)
    db.session.add(conversion)
    db.session.commit()
    assert conversion in subject.conversions.all()
    assert conversion in user.conversions.all()
    assert conversion in experiment.conversions.all()


def test_conversion_delete(db, conversion, user, experiment, subject):
    db.session.delete(conversion)
    db.session.commit()
    assert conversion not in subject.conversions.all()
    assert conversion not in user.conversions.all()
    assert conversion not in experiment.conversions.all()
