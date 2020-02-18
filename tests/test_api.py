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
def subject_id():
    return random.random()


def test_api_status(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_user_registration(client, email, password):
    resp = client.post('/user', data={
        'email': email,
        'password': password
    })
    assert resp.status_code == 200
    assert resp.json()['data']['token']['id'] is not None
    client.token = resp.json()['data']['token']['id']


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


def test_experiments_get(client, experiment_name):
    resp = client.get('/experiments')
    assert resp.status_code == 200
    assert resp.json()['data'][0]['name'] == experiment_name


def test_exposure_post(client, experiment_name, subject_id):
    resp = client.post('/exposures', data={
        'subject_id': subject_id,
        'experiment': experiment_name
    })
    assert resp.status_code == 200


def test_conversion_post(client, experiment_name, subject_id):
    resp = client.post('/conversions', data={
        'subject_id': subject_id,
        'experiment': experiment_name
    })
    assert resp.status_code == 200


def test_logging_out(client):
    client.logout()
    resp = client.get('/experiments')
    assert resp.status_code == 403
