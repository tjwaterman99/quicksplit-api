import datetime as dt
from uuid import uuid4

from app.models import Plan, Role, Scope, PlanSchedule


monthly_schedule_id = uuid4()
annual_schedule_id = uuid4()

plan_schedules = [
    PlanSchedule(id=monthly_schedule_id, name="monthly", interval=dt.timedelta(days=30)),
    PlanSchedule(id=annual_schedule_id, name="annual", interval=dt.timedelta(days=360)),
]

plans = [
    Plan(id=uuid4(), name="free",  price_in_cents=0, max_subjects_per_experiment=5000, max_active_experiments=3, schedule_id=None),

    Plan(id=uuid4(), name="developer",  price_in_cents=100*500, max_subjects_per_experiment=50000, max_active_experiments=10, schedule_id=monthly_schedule_id),

    Plan(id=uuid4(), name="developer",  price_in_cents=100*500*10, max_subjects_per_experiment=50000, max_active_experiments=10, schedule_id=annual_schedule_id),

    Plan(id=uuid4(), name="team",  price_in_cents=100*1500, max_subjects_per_experiment=100000, max_active_experiments=25, schedule_id=monthly_schedule_id),

    Plan(id=uuid4(), name="team",  price_in_cents=100*1500*10, max_subjects_per_experiment=100000, max_active_experiments=25, schedule_id=annual_schedule_id),

    Plan(id=uuid4(), name="custom",  price_in_cents=100 * 1000, max_subjects_per_experiment=500000, max_active_experiments=100, schedule_id=annual_schedule_id),
]

scopes = [
    Scope(id=uuid4(), name='staging'),
    Scope(id=uuid4(), name='production')
]

roles = [
    Role(id=uuid4(), name='admin'),
    Role(id=uuid4(), name='public'),
]
