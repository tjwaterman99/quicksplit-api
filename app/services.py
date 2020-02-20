import pandas as pd
import researchpy as rp
from statsmodels.formula.api import ols
from flask import g

from app.models import db
from app.sql import experiment_loader_query


class ExperimentResultCalculator(object):
    def __init__(self, experiment):
        self.experiment = experiment
        self.data = None
        self._anova = None
        self.scope_name = g.token.scope.name if hasattr(g, 'token') else 'production'

    def load_exposures(self):
        if self.data is None:
            query = experiment_loader_query.format(experiment_id=self.experiment.id, scope_name=self.scope_name)
            self.data = pd.DataFrame(db.session.execute(query))
            self.data.columns = ['name', 'subject', 'cohort', 'converted', 'conversion_value']
        return self.data

    # TODO: format this
    def _summary_table(self, values=False):
        if self.data is None:
            self.load()
        if values:
            return rp.summary_cont(self.data.groupby('cohort').conversion_value)
        else:
            return rp.summary_cont(self.data.groupby('cohort').converted)

    def anova(self, values=False):
        if self.data is None:
            self.load()
        if values:
            return ols('conversion_value ~ C(cohort)', data=self.data).fit()
        else:
            return ols('converted ~ C(cohort)', data=self.data).fit()
