from app.models import User, Experiment, Conversion


def test_root_index(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_user_get(db, client, user):
    db.session.add(user)
    db.session.commit()
    resp = client.get('/user')
    assert resp.status_code == 200
    assert User.query.get(resp.json['data']['id']) == user


def test_user_unauthorized_get(db, user, app):
    db.session.add(user)
    db.session.commit()
    client = app.test_client()
    resp = client.get('/user')
    assert resp.status_code == 403


def test_user_post(db, app):
    client = app.test_client()
    resp = client.post('/user', json={
        'email': 'tester@gmail.com',
        'password': 'password'
    })

    assert resp.status_code == 200
    user = User.query.get(resp.json['data']['id'])
    assert user is not None


def test_experiment_get(db, client, experiment):
    db.session.add(experiment)
    db.session.commit()
    resp = client.get('/experiments')
    assert resp.status_code == 200
    assert type(resp.json['data']) == list
    assert len(resp.json['data']) == 1
    assert str(experiment.id) == resp.json['data'][0]['id']


def test_experiment_id_get(db, client, experiment):
    db.session.add(experiment)
    db.session.commit()
    resp = client.get(f'/experiments/{str(experiment.id)}')
    assert resp.status_code == 200
    assert resp.json['data']['id'] == str(experiment.id)


def test_experiment_post(db, client):
    resp = client.post('/experiments', json={
        'name': "My first experiment"
    })
    assert resp.status_code == 200
    assert Experiment.query.get(resp.json['data']['id']) is not None


def test_experiment_post_over_active_limits(db, client, user):
    for name in range(user.account.plan.max_active_experiments + 1):
        resp = client.post('/experiments', json={'name': str(name)})
        assert resp.status_code == 200
        assert Experiment.query.get(resp.json['data']['id']) is not None

    experiments = user.experiments.all()
    assert len(experiments) == user.account.plan.max_active_experiments + 1
    assert len(list(filter(lambda x: x.active, experiments))) == user.account.plan.max_active_experiments
    assert len(list(filter(lambda x: not x.active, experiments))) == 1


def test_exposures_post(db, client, experiment, subject, cohort):
    db.session.add_all([experiment])
    db.session.commit()
    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'cohort': cohort.name
    })
    assert resp.status_code == 200
    assert experiment.exposures.count() == 1


def test_exposures_post_duplicate(db, client, experiment, cohort, subject):
    db.session.add(experiment)
    db.session.commit()
    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'cohort': cohort.name
    })
    assert resp.status_code == 200

    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'cohort': cohort.name
    })
    assert resp.status_code == 200
    assert experiment.exposures.count() == 1
    assert experiment.subjects_counter == 1
    assert experiment.user.account.subjects.count() == 1


def test_exposures_post_duplicate_subject(db, client, experiment, subject, cohort):
    experiment2_name = experiment.name + "new experiment"
    experiment2 = Experiment(name=experiment2_name, user=experiment.user)
    experiment2.activate()
    db.session.add_all([experiment, experiment2, subject, cohort])
    db.session.commit()
    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'cohort': cohort.name
    })
    assert resp.status_code == 200
    assert experiment.user.account.subjects.count() == 1

    resp = client.post('/exposures', json={
        'experiment': experiment2.name,
        'subject': subject.name,
        'cohort': cohort.name
    })
    assert resp.status_code == 200
    assert experiment.exposures.count() == 1
    assert experiment2.exposures.count() == 1
    assert experiment.user.account.subjects.count() == 1


def test_exposures_post_subject_limits(db, client, experiment, subject, cohort):
    experiment.user.account.plan.max_subjects_per_experiment = 1
    db.session.add_all([experiment, subject, cohort])
    db.session.commit()

    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'cohort': cohort.name
    })
    assert resp.status_code == 200

    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name + 'v2',
        'cohort': cohort.name
    })
    assert resp.status_code == 422
    assert experiment.exposures.count() == 1
    assert experiment.subjects_counter == 1
    assert experiment.user.account.subjects.count() == 1


def test_exposures_post_inactive_experiment(db, client, experiment):
    experiment.deactivate()
    db.session.add(experiment)
    db.session.commit()
    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': 'subject_name',
        'cohort': 'cohort_name'
    })
    assert resp.status_code == 422
    assert experiment.exposures.count() == 0
    assert experiment.subjects_counter == 0
    assert experiment.user.account.subjects.count()  == 0


def test_conversions_post(db, client, experiment, subject, exposure):
    db.session.add(exposure)
    db.session.commit()
    resp = client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'value': 30.0
    })
    assert resp.status_code == 200
    db.session.refresh(exposure)
    assert exposure.conversion is not None
    assert exposure.conversion.value == 30.0


def test_conversions_post_duplicate(db, client, experiment, exposure, subject):
    db.session.add(experiment)
    db.session.add(exposure)
    db.session.commit()
    resp = client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'value': 30.0
    })
    assert resp.status_code == 200
    db.session.refresh(exposure)
    assert exposure.conversion is not None
    assert exposure.conversion.value == 30.0

    resp = client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'value': 15.0
    })
    db.session.refresh(exposure)
    assert resp.status_code == 200
    assert exposure.conversion.value == 30.0


# Conversions should still be recorded for an inactive experiment
def test_conversions_post_inactive_experiment(db, client, experiment, exposure, conversion, subject):
    # This won't update the subjects counter on the experiment. We should
    # Really move the business logic from the resource to the model
    experiment.deactivate()
    db.session.add_all([experiment, exposure])
    db.session.commit()
    resp = client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'value': 15.0
    })
    assert resp.status_code == 200
    db.session.refresh(exposure)
    assert exposure.conversion.value == conversion.value


def test_results_get(db, client, experiment):
    db.session.add(experiment)
    db.session.commit()
    resp = client.get('/results', json={
        'experiment': experiment.name
    })
    assert resp.status_code == 200
    assert resp.json['data']['id'] == str(experiment.id)


def test_activation_resources(db, client, experiment):
    db.session.add(experiment)
    db.session.commit()
    resp = client.post('/deactivate', json={
        'experiment': experiment.name
    })
    assert resp.status_code == 200
    db.session.refresh(experiment)
    assert experiment.active == False

    resp = client.post('/activate', json={
        'experiment': experiment.name
    })
    assert resp.status_code == 200
    db.session.refresh(experiment)
    assert experiment.active == True
