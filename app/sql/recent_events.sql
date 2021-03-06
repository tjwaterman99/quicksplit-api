with recent_exposures as (
select
    exposure.id,
    'exposure' as type,
    experiment.name as experiment,
    cohort.name as cohort,
    subject.name as subject,
    null::float as value,
    exposure.last_seen_at
from exposure
join experiment on exposure.experiment_id = experiment.id
join cohort on cohort.id = exposure.cohort_id
join subject on exposure.subject_id = subject.id
join scope on scope.id = exposure.scope_id
where experiment.user_id = '{user_id}'
    and scope.name = '{scope_name}'
order by exposure.last_seen_at desc
limit 10),

recent_conversions as (
select
    conversion.id,
    'conversion' as type,
    experiment.name as experiment,
    cohort.name as cohort,
    subject.name as subject,
    conversion.value as value,
    conversion.last_seen_at
from exposure
join experiment on exposure.experiment_id = experiment.id
join cohort on cohort.id = exposure.cohort_id
join subject on exposure.subject_id = subject.id
join conversion on conversion.exposure_id = exposure.id
join scope on scope.id = exposure.scope_id
    and scope.name = '{scope_name}'
where experiment.user_id = '{user_id}'
order by conversion.last_seen_at desc
limit 10),

recent_agg as (
    select id, type, experiment, cohort, subject, value, last_seen_at
    from recent_exposures
    union
    select id, type, experiment, cohort, subject, value, last_seen_at
    from recent_conversions
)

select * from
recent_agg
order by recent_agg.last_seen_at desc
limit 15
