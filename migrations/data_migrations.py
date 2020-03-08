import datetime as dt
import inspect
from uuid import uuid4

from flask import current_app

from app.models import db, Plan, PlanSchedule
from app.seeds import plan_schedules, monthly_schedule_id, annual_schedule_id


def print_revision_function_name():
    current_frame = inspect.currentframe()
    call_frame = inspect.getouterframes(current_frame, 1)
    print(f"Running data migration: {call_frame[1][3]}")


def revision_8916265b8931_up():
    print_revision_function_name()
    db.session.add_all(plan_schedules)
    db.session.flush()

    current_plans = Plan.query.all()
    for plan in current_plans:
        if plan.name in ('free'):
            plan.schedule_id = None
        elif plan.name in ('developer', 'team'):
            plan.schedule_id = monthly_schedule_id
        elif plan.name in ('custom'):
            plan.schedule_id = annual_schedule_id
        else:
            print(f"Unknown plan name: {plan.name}")


def revision_8916265b8931_down():
    print_revision_function_name()
    db.session.execute('update plan set schedule_id=null')
    db.session.execute('delete from plan_schedule where 1=1')
    db.session.commit()


def revision_a7478a966ea0_up():
    print_revision_function_name()
    annual_schedule_id = PlanSchedule.query.filter(PlanSchedule.name=='annual').first().id
    plans = [
        Plan(id=uuid4(), name="team",  price_in_cents=100*250, max_subjects_per_experiment=100000, max_active_experiments=25, schedule_id=annual_schedule_id),
        Plan(id=uuid4(), name="developer",  price_in_cents=100*50, max_subjects_per_experiment=50000, max_active_experiments=10, schedule_id=annual_schedule_id),
    ]
    db.session.add_all(plans)
    db.session.commit()


def revision_a7478a966ea0_down():
    print_revision_function_name()
    annual_schedule_id = PlanSchedule.query.filter(PlanSchedule.name=='annual').first().id
    plans = Plan.query.filter(Plan.name.in_(['developer', 'team'])) \
                      .filter(Plan.schedule_id==annual_schedule_id) \
                      .all()
    for plan in plans:
        db.session.delete(plan)
    db.session.commit()


def revision_99ab26e65607_up():
    # Make sure annual plans have higher prices
    print_revision_function_name()
    annual_schedule_id = PlanSchedule.query.filter(PlanSchedule.name=='annual').first().id
    plans = Plan.query.filter(Plan.name.in_(['team', 'developer'])) \
                      .filter(Plan.schedule_id==annual_schedule_id) \
                      .all()
    for plan in plans:
        plan.price_in_cents = plan.price_in_cents * 10
    db.session.add_all(plans)
    db.session.commit()


def revision_99ab26e65607_down():
    print_revision_function_name()
    annual_schedule_id = PlanSchedule.query.filter(PlanSchedule.name=='annual').first().id
    plans = Plan.query.filter(Plan.name.in_(['team', 'developer'])) \
                      .filter(Plan.schedule_id==annual_schedule_id) \
                      .all()
    for plan in plans:
        plan.price_in_cents = int(plan.price_in_cents / 10)
    db.session.add_all(plans)
    db.session.commit()
