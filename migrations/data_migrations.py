import inspect

from flask import current_app

from app.models import db, Plan
from app.seeds import plan_schedules, monthly_schedule_id, annual_schedule_id


def print_revision_function_name():
    current_frame = inspect.currentframe()
    call_frame = inspect.getouterframes(current_frame, 1)
    print(f"Running data migration: {call_frame[1][3]}")


def revision_63839d762be5():
    print_revision_function_name()


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
