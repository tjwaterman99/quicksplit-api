select
  experiment_result.*,
  experiment.name as experiment_name,
  case when ran_at is not null then true else false end as ran
from experiment_result
join experiment on experiment_result.experiment_id=experiment.id
where experiment_result.user_id='{user_id}'
