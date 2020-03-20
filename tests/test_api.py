"""
A set of tests for validating the web api. Uses the environment variable
QUICK_SPLIT_API_URL for selecting which api to test.

To test against a production api, you could run:

    docker-compose run -e QUICKSPLIT_API_URL=https://quick-split.herokuapp.com  --rm web pytest tests/test_api.py

Note that the order of the tests is important.
"""

import os
import random
import datetime as dt

import requests
import pytest


class Client(object):
    def __init__(self, url=None):
        self.url = url or os.environ['QUICKSPLIT_API_URL']
        self.token = None

    def logout(self):
        self.token = None

    def send(self, method, route, data):
        route  = self.url  + route
        headers = {}
        if self.token:
            headers.update({'Authorization': self.token})
        return requests.request(method, route, json=data, headers=headers)

    def get(self, route, data=None):
        return self.send(method='GET', route=route, data=data)

    def post(self, route, data=None):
        return self.send(method='POST', route=route, data=data)


@pytest.fixture(scope='module')
def client():
    return Client()


@pytest.fixture(scope='module')
def email():
    return f'tester-{dt.datetime.now().timestamp()}@quicksplit.io'


@pytest.fixture(scope='module')
def password():
    return f'{random.random()}'


@pytest.fixture(scope='module')
def experiment_name():
    return 'my-test-experiment'


@pytest.fixture(scope='module')
def subject_name():
    return random.random()


@pytest.fixture(scope='module')
def cohort_name():
    return 'experimental'


def test_api_status(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_plans_get(client):
    resp = client.get('/plans')
    assert resp.status_code == 200


def test_user_registration(client, email, password):
    resp = client.post('/user', data={
        'email': email,
        'password': password
    })
    assert resp.status_code == 200
    assert resp.json()['data']['tokens'][0] is not None
    client.token = resp.json()['data']['tokens'][0]['value']


def test_user_get(client):
    resp = client.get('/user')
    assert resp.status_code == 200
    assert resp.json()['data']['id'] is not None


def test_experiments_post(client, experiment_name):
    resp = client.post('/experiments', data={
        'name': experiment_name
    })
    assert resp.status_code == 200
    assert resp.json()['data']['id'] is not None


def test_experiments_duplicate_post(client, experiment_name):
    resp = client.post('/experiments', data={
        'name': experiment_name
    })
    assert resp.status_code == 403

    resp = client.get('/experiments')
    assert resp.status_code == 200


def test_experiments_get(client, experiment_name):
    resp = client.get('/experiments')
    assert resp.status_code == 200
    assert resp.json()['data'][0]['name'] == experiment_name


def test_exposure_post(client, experiment_name, subject_name, cohort_name):
    resp = client.post('/exposures', data={
        'subject': subject_name,
        'experiment': experiment_name,
        'cohort': cohort_name
    })
    assert resp.status_code == 200
    assert resp.json()['data']['experiment']['subjects_counter'] == 1


def test_exposure_post_duplicate(client, experiment_name, subject_name, cohort_name):
    resp = client.post('/exposures', data={
        'subject': subject_name,
        'experiment': experiment_name,
        'cohort': cohort_name
    })
    assert resp.status_code == 200
    assert resp.json()['data']['experiment']['subjects_counter'] == 1


def test_exposure_post_non_duplicate(client, experiment_name, subject_name, cohort_name):
    resp = client.post('/exposures', data={
        'subject': subject_name * 2,
        'experiment': experiment_name,
        'cohort': cohort_name
    })
    assert resp.status_code == 200
    assert resp.json()['data']['experiment']['subjects_counter'] == 2


def test_conversion_post(client, experiment_name, subject_name):
    resp = client.post('/conversions', data={
        'subject': subject_name,
        'experiment': experiment_name,
        'value': 60.0
    })
    assert resp.status_code == 200


def test_deactivation_post(client, experiment_name):
    resp = client.post('/deactivate',  data={
        'experiment': experiment_name
    })
    assert resp.status_code == 200
    assert resp.json()['data']['active'] == False


def test_activation_post(client, experiment_name):
    resp = client.post('/activate',  data={
        'experiment': experiment_name
    })
    assert resp.status_code == 200
    assert resp.json()['data']['active'] == True


def test_results_get_before_result_create(client, experiment_name):
    resp = client.get('/results')
    assert resp.status_code == 200
    assert resp.json()['data'] == []


def test_results_post(client, experiment_name, cohort_name):
    resp = client.post('/results', data={
        'experiment': experiment_name
    })
    assert resp.status_code == 200
    assert resp.json()['data']['ran'] == True
    assert resp.json()['data']['fields']['table'][0]['cohort'] == cohort_name
    assert resp.json()['data']['fields']['summary'] is not None


def test_logging_out(client):
    client.logout()
    resp = client.get('/experiments')
    assert resp.status_code == 403
