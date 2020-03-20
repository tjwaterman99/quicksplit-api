from dataclasses import dataclass
from typing import List, Dict, Union

import pandas as pd
import researchpy as rp
from statsmodels.formula.api import ols
from flask import g
import numpy as np

from app.models import db, Experiment, Scope
from app.sql import experiment_loader_query


@dataclass
class ExperimentResultCalculator(object):
    experiment: Experiment
    scope: Scope
    experiment_name: str
    scope_name: str
    table: List[Dict]
    summary: str

    subjects: int
    significant: bool


    def __init__(self, experiment, scope):
        self.experiment = experiment
        self.scope = scope

        self.data = None
        self.df = None
        self.model = None

    def load_data(self):
        if self.data is None:
            query = experiment_loader_query.format(experiment_id=self.experiment.id, scope_id=self.scope.id)
            self.data = pd.DataFrame(db.session.execute(query))
            self.data.columns = ['name', 'subject', 'cohort', 'converted', 'conversion_value']
        return self.data

    def load_df(self):
        if self.data is None:
            self.load_data()
        if self.df is None:
            self.df = rp.summary_cont(self.data.groupby('cohort').converted)
        return self.df

    def load_model(self):
        if self.data is None:
            self.load_data()
        if self.model is None:
            self.model = ols('converted ~ C(cohort)', data=self.data).fit()
        return self.model

    def run(self):
        self.load_data()
        self.load_df()
        self.load_model()
        self.loaded = True

    @property
    def scope_name(self):
        return self.scope.name

    @property
    def experiment_name(self):
        return self.experiment.name

    @property
    def summary(self):
        if not self.loaded:
            self.run()
        return str(self.model.summary())

    @property
    def table(self):
        cdf = self.df.reset_index()
        cdf.columns = ['cohort', 'subjects', 'conversion rate', 'sd', 'se', 'lci', 'rci']
        ci_df = cdf[['lci', 'rci']].round(3).fillna("").applymap(lambda x: str(x))

        # Create CI's in a single column
        ci = "[" + ci_df.lci + ',' + ci_df.rci + ']'
        ci.name = "95% Conf. Interval"

        cdf['conversion rate'] = cdf['conversion rate'].round(3)
        result = cdf[['cohort', 'subjects', 'conversion rate']].join(ci).fillna("")
        return result.to_dict(orient='records')

    @property
    def pvalue(self):
        if self.model.f_pvalue == np.nan:
            return None
        elif self.model.f_pvalue >= 0:
            return float(self.model.f_pvalue)
        else:
            return None

    @property
    def significant(self):
        if self.pvalue:
            return self.pvalue < 0.1

    @property
    def subjects(self):
        return self.model.nobs
