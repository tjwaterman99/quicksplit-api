select
    experiment.name,
    subject.name as subject,
    cohort.name as cohort,
    case when conversion.id is null then 0 else 1 end as converted,
    conversion.value as conversion_value
from experiment
join exposure on experiment.id = exposure.experiment_id
join subject on exposure.subject_id = subject.id
join cohort on exposure.cohort_id = cohort.id
join scope on exposure.scope_id = scope.id
left join conversion on conversion.exposure_id = exposure.id
where experiment.id = '{experiment_id}'::uuid
    and scope.id = '{scope_id}'
