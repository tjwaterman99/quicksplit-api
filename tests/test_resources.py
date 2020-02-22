from flask import request
from pytest import raises

from app.resources import params
from app.models import User, Experiment, Exposure, Conversion, Scope
from app.exceptions import ApiException


def test_params_decorator(app):

    @params('needed', option=5)
    def test(*args, **kwargs):
        return kwargs

    with app.test_request_context(json={'needed': True}):
        assert test() == {'needed': True, 'option': 5}

    with app.test_request_context(json={'needed': True, 'option': 1}):
        assert test() == {'needed': True, 'option': 1}

    with app.test_request_context(json={'option': 1}):
        with raises(ApiException) as exc:
            test()
        assert exc.value.status_code == 422
        assert 'needed' in exc.value.message

    with app.test_request_context(json={'notallowed': 'value', 'needed': True}):
        with raises(ApiException) as exc:
            test()
        assert exc.value.status_code == 422
        assert 'notallowed' in exc.value.message


def test_root_index(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_user_get(db, client, user):
    resp = client.get('/user')
    assert resp.status_code == 200


def test_user_unauthorized_get(db, user, app):
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


def test_experiment_get(db, client, experiment):
    resp = client.get('/experiments')
    assert resp.status_code == 200
    assert type(resp.json['data']) == list
    assert len(resp.json['data']) == 1
    assert str(experiment.id) == resp.json['data'][0]['id']


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
    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'cohort': cohort.name
    })
    assert resp.status_code == 200
    assert experiment.exposures.count() == 1


def test_exposures_post_duplicate(db, client, experiment, cohort, subject):
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
    db.session.flush()
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
    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'cohort': cohort.name
    })
    assert resp.status_code == 200
    assert experiment.exposures.count() == 1

    resp = client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': subject.name + 'v2',
        'cohort': cohort.name
    })
    experiment = db.session.query(Experiment).first()
    assert resp.status_code == 422
    assert experiment.exposures.count() == 1
    assert experiment.subjects_counter == 1
    assert experiment.user.account.subjects.count() == 1


def test_exposures_post_inactive_experiment(db, client, experiment):
    experiment.deactivate()
    db.session.add(experiment)
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
    resp = client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'value': 15.0
    })
    assert resp.status_code == 200
    db.session.refresh(exposure)
    assert exposure.conversion.value == conversion.value


def test_results_get(db, client, experiment, exposure):
    resp = client.get('/results', json={
        'experiment': experiment.name
    })
    assert resp.status_code == 200
    assert resp.json['data']['experiment']['name'] == str(experiment.name)
    assert resp.json['data']['scope_name'] == 'production'
    assert resp.json['data']['subjects'] == 1
    assert resp.json['data']['significant'] == None
    assert len(resp.json['data']['table']) == 1


def test_activation_resources(db, client, experiment):
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


def test_tokens_resource(db, client, user):
    resp = client.get('/tokens')
    assert resp.status_code == 200
    assert resp.json['data'][0]['id'] == str(user.tokens[0].id)
    assert len(resp.json['data']) == 4
    assert resp.json['data'][0]['private'] == True


def test_staging_client_inserts_to_staging(db, admin_staging_client, user, experiment):
    resp = admin_staging_client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': 'subject_name',
        'cohort': 'cohort_name'

    })
    assert resp.status_code == 200
    exposure = Exposure.query.first()

    assert exposure is not None
    assert exposure.scope.name == 'staging'

    resp = admin_staging_client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': 'subject_name',
    })
    assert resp.status_code == 200
    conversion = Conversion.query.first()

    assert conversion is not None
    assert conversion.scope.name == 'staging'


def test_public_staging_client_inserts(db, public_staging_client, user, experiment):
    resp = public_staging_client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': 'subject_name',
        'cohort': 'cohort_name'

    })
    assert resp.status_code == 200
    exposure = Exposure.query.first()

    assert exposure is not None
    assert exposure.scope.name == 'staging'

    resp = public_staging_client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': 'subject_name',
    })
    assert resp.status_code == 200
    conversion = Conversion.query.first()

    assert conversion is not None
    assert conversion.scope.name == 'staging'


def test_public_production_client_inserts(db, public_production_client, user, experiment):
    resp = public_production_client.post('/exposures', json={
        'experiment': experiment.name,
        'subject': 'subject_name',
        'cohort': 'cohort_name'
    })
    assert resp.status_code == 200
    exposure = Exposure.query.first()

    assert exposure is not None
    assert exposure.scope.name == 'production'

    resp = public_production_client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': 'subject_name',
    })
    assert resp.status_code == 200
    conversion = Conversion.query.first()

    assert conversion is not None
    assert conversion.scope.name == 'production'


def test_recent_get(db, client, experiment, exposure, conversion):
    resp = client.get('/recent')

    assert resp.status_code == 200
    assert len(resp.json['data']) == 2


def test_staging_recent_get(db, client, admin_staging_client, experiment):
    resp = admin_staging_client.get('/recent')
    assert resp.status_code == 200
    assert len(resp.json['data']) == 0

    exp_resp = admin_staging_client.post('/exposures', json={
        'experiment': experiment.name,
        'cohort': 'tester',
        'subject': 'tester1'
    })
    assert exp_resp.status_code == 200

    resp2 = admin_staging_client.get('/recent')
    assert resp2.status_code == 200
    assert len(resp2.json['data']) == 1

    resp3 = client.get('/recent')
    assert resp3.status_code == 200
    assert  len(resp3.json['data']) == 0
