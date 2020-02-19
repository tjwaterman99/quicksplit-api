import pytest

from app.services import ExperimentResultCalculator

import logging


@pytest.fixture
def exposures_count():
    return 50


@pytest.fixture
def setup_experiment(client, experiment, exposures_count):
    for n in range(exposures_count):
        cohort = 'experimental' if n % 2 == 0 else 'control'
        subject = f'subject-{n}'
        resp = client.post('/exposures', json={
            'cohort': cohort,
            'subject': subject,
            'experiment': experiment.name
        })

        if resp.status_code != 200:
            logging.error(resp.json)
            raise AttributeError

        resp = client.post('/conversions', json={
            'subject': subject,
            'experiment': experiment.name,
            'value': n / 5
        })

        if resp.status_code != 200:
            logging.error(resp.json)
            raise AttributeError


def test_experiment_result_calculator(db, setup_experiment, experiment, exposures_count):
    erc = ExperimentResultCalculator(experiment)
    erc.load_exposures()
    assert len(erc.data) == exposures_count
