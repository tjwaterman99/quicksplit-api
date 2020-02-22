import pytest

from app.services import ExperimentResultCalculator

import logging


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


def test_experiment_result_calculator_50_samples(db, client, experiment):
    exposures_count = 50
    setup_experiment(client, experiment, exposures_count)
    erc = ExperimentResultCalculator(experiment)
    erc.run()
    assert erc.subjects == exposures_count
    assert erc.pvalue is not None


def test_experiment_result_calculator_1_sample(db, client, experiment):
    exposures_count = 1
    setup_experiment(client, experiment, exposures_count)
    erc = ExperimentResultCalculator(experiment)
    erc.run()
    assert erc.subjects == exposures_count
    assert erc.pvalue is None


def test_experiment_result_calculator_5_samples(db, client, experiment):
    exposures_count = 5
    setup_experiment(client, experiment, exposures_count)
    erc = ExperimentResultCalculator(experiment)
    erc.run()
    assert erc.subjects == exposures_count
    assert erc.pvalue is not None
