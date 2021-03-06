from flask import request
from pytest import raises

from app.resources import params
from app.models import User, Experiment, Exposure, Conversion, Scope, Contact, Subject, Cohort
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

    with app.test_request_context():
        with raises(ApiException) as exc:
            test()
        assert exc.value.status_code == 422


def test_root_index(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_404_error_code(client):
    resp = client.get('/thisroutewillneverexist')
    assert resp.status_code == 404


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


def test_experiment_post_duplicate(db, client, experiment):
    resp = client.post('/experiments', json={
        'name': experiment.name
    })
    assert resp.status_code == 403


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
    # We can't test the subjects_counter incrementing logic because both tests
    # are using a single db transaction, which breaks the logic as it relies
    # on the ON CONFLICT DO UPDATE statement
    # assert experiment.subjects_counter == 1
    assert experiment.user.account.subjects.count() == 1


# TODO: this test needs a client set up to use the team_plan_user's tokens.
import pytest
@pytest.mark.skip
def test_exposures_post_duplicate_subject(db, team_plan_user, client, production_scope):
    experiment_1 = Experiment.create(name="first experiment", user=team_plan_user)
    experiment_2 = Experiment.create(name="second experiment", user=team_plan_user)
    db.session.add_all([experiment_1, experiment_2])
    db.session.flush()
    # This client is using the free user's tokens, not the team_plan_user's tokens
    resp = client.post('/exposures', json={
        'experiment': experiment_1.name,
        'subject': 'subject_name',
        'cohort': 'cohort_name'
    })
    assert resp.status_code == 200
    assert team_plan_user.account.subjects.count() == 1

    resp = client.post('/exposures', json={
        'experiment': experiment_2.name,
        'subject': 'subject_name',
        'cohort': 'cohort_name'
    })
    assert resp.status_code == 200
    assert experiment_1.exposures.count() == 1
    assert experiment_2.exposures.count() == 1
    assert team_plan_user.account.subjects.count() == 1


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
    experiment.deactivate()
    resp = client.post('/conversions', json={
        'experiment': experiment.name,
        'subject': subject.name,
        'value': 15.0
    })
    assert resp.status_code == 200
    assert exposure.conversion.value == conversion.value


def test_results_get(db, client, experiment, exposure, conversion, experiment_result):
    resp = client.get('/results')
    assert resp.status_code == 200
    assert len(resp.json['data']) == 1
    experiment_result_json = resp.json['data'][0]
    assert experiment_result_json['id'] == str(experiment_result.id)
    assert experiment_result_json['ran'] == False
    assert experiment_result_json['ran_at'] == None


def test_results_details_get(db, client, user, experiment_result):
    resp = client.get(f'/results/{experiment_result.id}')
    assert resp.status_code == 200
    assert resp.json['data']['id'] == str(experiment_result.id)


def test_results_get_ran_experiment_result(db, client, experiment, exposure, conversion, experiment_result):
    ran_experiment_result = experiment_result.run()
    resp = client.get('/results')
    assert resp.status_code == 200
    assert len(resp.json['data']) == 1
    experiment_result_json = resp.json['data'][0]
    assert experiment_result_json['id'] == str(experiment_result.id)
    assert experiment_result_json['ran'] == True
    assert experiment_result_json['ran_at'] != None


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

    assert resp.json['data'][0]['type'] == 'conversion'
    assert resp.json['data'][1]['type'] == 'exposure'

    # TODO: isoformat does not include timezones, which the json data includes
    assert str(conversion.last_seen_at.isoformat()) in resp.json['data'][0]['last_seen_at']
    assert str(exposure.last_seen_at.isoformat()) in resp.json['data'][1]['last_seen_at']


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


def test_events_resource_post(db, client, user):
    resp = client.post('/events', json={
        'name': "test event"
    })

    assert resp.status_code == 200
    assert resp.json['data']['id'] is not None
    assert resp.json['data']['name'] == 'test event'
    assert resp.json['data']['data'] == None
    assert resp.json['data']['user_id'] == None

    resp = client.post('/events', json={
        'name': "test event",
        'user_id': str(user.id)
    })

    assert resp.status_code == 200
    assert resp.json['data']['id'] is not None
    assert resp.json['data']['name'] == 'test event'
    assert resp.json['data']['data'] == None
    assert resp.json['data']['user_id'] == str(user.id)

    resp = client.post('/events', json={
        'name': "test event",
        'data': {'a': 1, 'b': 2, 'c': [4,5,6]}
    })

    assert resp.status_code == 200
    assert resp.json['data']['id'] is not None
    assert resp.json['data']['name'] == 'test event'
    assert resp.json['data']['data'] == {'a': 1, 'b': 2, 'c': [4,5,6]}
    assert resp.json['data']['user_id'] == None


def test_plans_resource_get(db, client, user):
    # Changing this number will break the front end styles
    expected_public_plan_count = 6
    resp = client.get("/plans")
    assert resp.status_code == 200
    assert len(resp.json['data']) == expected_public_plan_count


def test_contacts_resource_post(db, client, user):
    resp  = client.post('/contacts', json={
        'email': "tester",
        'message': "what's the news?",
        'subject':  "hello world"
    })
    assert resp.status_code == 200
    assert resp.json['data']['job']['id'] is not None
