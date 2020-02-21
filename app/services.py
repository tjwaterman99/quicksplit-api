import pandas as pd
import researchpy as rp
from statsmodels.formula.api import ols
from flask import g
import numpy as np

from app.models import db
from app.sql import experiment_loader_query


class ExperimentResultCalculator(object):
    def __init__(self, experiment, scope_name="production"):
        self.experiment = experiment
        self.scope_name = scope_name
        self.data = None
        self.model = None
        self.table = None
        self.loaded = False

    def load_data(self):
        if self.data is None:
            query = experiment_loader_query.format(experiment_id=self.experiment.id, scope_name=self.scope_name)
            self.data = pd.DataFrame(db.session.execute(query))
            self.data.columns = ['name', 'subject', 'cohort', 'converted', 'conversion_value']
        return self.data

    def load_table(self):
        if self.data is None:
            self.load_date()
        if self.table is None:
            self.table = rp.summary_cont(self.data.groupby('cohort').converted)
        return self.table

    def load_model(self):
        if self.data is None:
            self.load_data()
        if self.model is None:
            self.model = ols('converted ~ C(cohort)', data=self.data).fit()
        return self.model

    def run(self):
        self.load_data()
        self.load_table()
        self.load_model()
        self.loaded = True

    @property
    def table_json(self):
        return self.table.reset_index().to_dict(orient='records')

    @property
    def f_pvalue(self):
        print(self.model.f_pvalue)
        self.data.to_pickle("data.pickle")
        if self.model.f_pvalue == np.nan:
            return None
        elif self.model.f_pvalue >= 0:
            return float(self.model.f_pvalue)
        else:
            return None

    @property
    def significant(self):
        if self.f_pvalue:
            return self.f_pvalue < 0.1

    @property
    def nobs(self):
        return self.model.nobs
