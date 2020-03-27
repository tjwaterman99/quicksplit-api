select
    '{date}'::date as day,
    "user".id as user_id,
    account.id as account_id,
    experiment.id as experiment_id,
    experiment.name as experiment_name,
    exposure.scope_id as scope_id,
    count(exposure.id) as exposures,
    count(conversion.id) as conversions
from experiment
join "user" on experiment.user_id = "user".id
join account on "user".account_id = account.id
join exposure on exposure.experiment_id = experiment.id
    and exposure.last_seen_at::date = '{date}'::date
left join conversion on conversion.exposure_id = exposure.id
    and conversion.last_seen_at::date = '{date}'::date
group by 1,2,3,4,5,6
order by 1 desc
