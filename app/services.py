import pandas as pd
import researchpy as rp
from statsmodels.formula.api import ols

from app.models import db


experiment_loader_query = """
select
    experiment.name,
    subject.name as subject,
    cohort.name as cohort,
    case when conversion.id is null then 1 else 0 end as converted,
    conversion.value as conversion_value
from experiment
join exposure on experiment.id = exposure.experiment_id
join subject on exposure.subject_id = subject.id
join cohort on exposure.cohort_id = cohort.id
left join conversion on conversion.exposure_id = exposure.id
where experiment.id = '{experiment_id}'::uuid
"""


class ExperimentResultCalculator(object):
    def __init__(self, experiment):
        self.experiment = experiment
        self.data = None
        self._anova = None

    def load_exposures(self):
        if self.data is None:
            query = experiment_loader_query.format(experiment_id=self.experiment.id)
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
