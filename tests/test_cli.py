"""
A set of tests for validating the CLI. Note that the API used can be configured
via the environment variable QUICKSPLIT_API_URL.

To test against a production api, you could run:

    docker-compose run -e QUICKSPLIT_API_URL=https://quick-split.herokuapp.com  --rm web pytest tests/test_cli.py

Note that the order of the tests is important.
"""

import random
import subprocess
import os
import pytest


os.environ.setdefault('QUICKSPLIT_API_URL', 'http://web:5000')


@pytest.fixture(scope='module')
def email():
    return f"{random.random()}@gmail.com"


@pytest.fixture(scope='module')
def password():
    return "notsecure"


def test_cli_loads():
    assert subprocess.run('quicksplit').returncode == 0


def test_cli_registers(email, password):
    cmd = f'quicksplit register --email {email} --password {password}'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert email in resp.stdout.decode()


def test_cli_registers_email(email):
    cmd = ['quicksplit', 'whoami']
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert email in resp.stdout.decode()


def test_cli_uses_correct_url():
    cmd = ['quicksplit', 'config']
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert os.environ['QUICKSPLIT_API_URL'] in resp.stdout.decode()


def test_cli_can_create_experiment():
    cmd = ['quicksplit', 'create', '--name', 'mytestexperiment']
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert 'mytestexperiment' in resp.stdout.decode()


def test_cli_can_list_experiments():
    cmd = ['quicksplit', 'experiments']
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert 'mytestexperiment' in resp.stdout.decode()
