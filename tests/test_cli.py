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
import json

from cli.printers import Printer

os.environ.setdefault('QUICKSPLIT_API_URL', 'http://web:5000')

"""
  config       Print configuration information used by the client
  create       Create a new experiment
  experiments  List active experiments
  log          Create a new exposure or conversion event
  X login        Log in to quicksplit.io
  recent       Display recent exposure and conversion events
  register     Create a new account on quicksplit.io
  results      Print the results of an experimence
  X start        Start a stopped experiment
  X stop         Stop an active experiment
  X tokens       Print the set of available tokens
  X whoami       Print the email address of the current account
"""


@pytest.fixture(scope='module')
def email():
    return f"{random.random()}@gmail.com"


@pytest.fixture(scope='module')
def password():
    return "notsecure"


@pytest.fixture(scope='module')
def experiment_name():
    return 'mytestexperiment'


def test_cli_loads():
    assert subprocess.run('quicksplit').returncode == 0


def test_cli_handles_errors():
    cmd = 'quicksplit whoami'.split()
    assert subprocess.run(cmd).returncode == 0

    cmd = 'quicksplit login --email invalid --password invalid'.split()
    assert subprocess.run(cmd).returncode == 0

    cmd = 'quicksplit experiments'.split()
    assert subprocess.run(cmd).returncode == 0

    cmd = 'quicksplit tokens'.split()
    assert subprocess.run(cmd).returncode == 0


def test_cli_registers(email, password):
    cmd = f'quicksplit register --email {email} --password {password}'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert email in resp.stdout.decode()


def test_cli_handles_logins_of_nonvalid_users(email, password):
    cmd = 'quicksplit login --email dns --password dne'.split()
    assert subprocess.run(cmd).returncode == 0


def test_cli_handles_invalid_login_password(email, password):
    cmd = f'quicksplit login --email {email} --password wrong'.split()
    assert subprocess.run(cmd).returncode == 0


def test_cli_handles_valid_logins(email, password):
    cmd = f'quicksplit register --email {email}2 --password {password}'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert email + '2' in resp.stdout.decode()

    cmd = f'quicksplit login --email {email} --password {password}'.split()
    assert subprocess.run(cmd).returncode == 0


def test_cli_lists_tokens():
    cmd = 'quicksplit tokens'.split()
    resp = subprocess.run(cmd)
    assert resp.returncode == 0


def test_cli_prints_current_token():
    cmd = 'quicksplit tokens --current'.split()
    resp = subprocess.run(cmd)
    assert resp.returncode == 0


def test_cli_logs_config_as_json(email):
    cmd = 'quicksplit config'.split()
    resp = subprocess.run(cmd, capture_output=True)
    config = json.loads(resp.stdout.decode())
    assert 'user' in config
    assert 'token' in config
    assert 'api_url' in config
    assert config['api_url'] == os.environ['QUICKSPLIT_API_URL']
    assert 'email' in config['user']
    assert config['user']['email'] == email
    assert len(config['user']['tokens']) == 4


def test_cli_registers_email(email):
    cmd = ['quicksplit', 'whoami']
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert email == resp.stdout.decode().strip()


def test_cli_uses_correct_url():
    cmd = ['quicksplit', 'config']
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert os.environ['QUICKSPLIT_API_URL'] in resp.stdout.decode()


def test_cli_handles_nonexisting_experiments():
    cmd = 'quicksplit experiments'.split()
    assert subprocess.run(cmd, capture_output=True).returncode == 0

    cmd = 'quicksplit recent'.split()
    assert subprocess.run(cmd, capture_output=True).returncode == 0

    cmd = 'quicksplit results tester'.split()
    assert subprocess.run(cmd, capture_output=True).returncode == 0

    cmd = 'quicksplit log exposure -e tester -c exp -s 1234'.split()
    assert subprocess.run(cmd, capture_output=True).returncode == 0

    cmd = 'quicksplit log exposure -e tester -c exp -s 1234 --staging'.split()
    assert subprocess.run(cmd, capture_output=True).returncode == 0

    cmd = 'quicksplit log conversion -e tester -s 1234'.split()
    assert subprocess.run(cmd, capture_output=True).returncode == 0

    cmd = 'quicksplit log conversion -e tester -s 1234 --staging'.split()
    assert subprocess.run(cmd, capture_output=True).returncode == 0


def test_cli_can_create_experiment(experiment_name):
    cmd = ['quicksplit', 'create', experiment_name]
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert experiment_name in resp.stdout.decode()


def test_cli_can_list_experiments(experiment_name):
    cmd = ['quicksplit', 'experiments']
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert experiment_name in resp.stdout.decode()


def test_cli_can_stop_experiments(experiment_name):
    cmd = ['quicksplit', 'stop', experiment_name]
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert experiment_name in resp.stdout.decode()
    assert 'Stopped' in resp.stdout.decode()


def test_cli_can_start_experiments(experiment_name):
    cmd = ['quicksplit', 'start', experiment_name]
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert experiment_name in resp.stdout.decode()
    assert 'Started' in resp.stdout.decode()


def test_cli_can_log_exposures(experiment_name):
    cmd = f'quicksplit log exposure -s 12345 -c control -e {experiment_name}'.split()
    assert subprocess.run(cmd).returncode == 0

    cmd = f'quicksplit log exposure -s 12345 -c control -e {experiment_name} --staging'.split()
    assert subprocess.run(cmd).returncode == 0


def test_cli_can_log_conversions(experiment_name):
    cmd = f'quicksplit log conversion -s 12345 -e {experiment_name}'.split()
    assert subprocess.run(cmd).returncode == 0

    cmd = f'quicksplit log conversion -s 12345 -e {experiment_name} --staging'.split()
    assert subprocess.run(cmd).returncode == 0


def test_cli_can_list_results(experiment_name):
    cmd = f'quicksplit results {experiment_name}'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert 'control' in resp.stdout.decode()

    cmd = f'quicksplit results {experiment_name} --staging'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert 'control' in resp.stdout.decode()


def test_cli_can_list_recent(experiment_name):
    cmd = f'quicksplit recent'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert experiment_name in resp.stdout.decode()

    cmd = f'quicksplit recent --staging'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert experiment_name in resp.stdout.decode()


def test_cli_can_logout():
    cmd = f'quicksplit logout'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0

    cmd = f'quicksplit experiments'.split()
    resp = subprocess.run(cmd, capture_output=True)
    assert resp.returncode == 0
    assert '403' in resp.stdout.decode()



def test_printer():
    input = [{"a": 1, "b": 2, "c": 3}, {"a": 3, "b": 4, "c": 5}]
    printer = Printer(input, bold_header=False, color=None)
    assert printer.table_data == [['a','b', 'c'], [1,2,3], [3,4,5]]

    printer = Printer(input, order=['b','c'], bold_header=False, color=None)
    assert printer.table_data == [['b', 'c'], [2,3], [4,5]]

    printer = Printer(input, order=['b','a','c'], bold_header=False, color=None)
    assert printer.table_data == [['b','a','c'], [2,1,3], [4,3,5]]
