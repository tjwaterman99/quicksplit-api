import datetime as dt
import inspect
from uuid import uuid4

from flask import current_app

from app.models import db, Plan, PlanSchedule, Account
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


# Raise prices (developer = $500/mo, team = $1500/mo)
def revision_6e332fd22e34_up():
    print_revision_function_name()
    developer_plans = Plan.query.filter(Plan.name=="developer").all()
    for plan in developer_plans:
        plan.price_in_cents = plan.price_in_cents  * 10   # change  from $50/mo -> $500/mo
        db.session.add(plan)

    team_plans = Plan.query.filter(Plan.name=="team").all()
    for plan in team_plans:
        plan.price_in_cents = plan.price_in_cents * 6  # change from $250/mo -> $1,500/mo
        db.session.add(plan)
    db.session.commit()


def revision_6e332fd22e34_down():
    print_revision_function_name()
    developer_plans = Plan.query.filter(Plan.name=="developer").all()
    for plan in developer_plans:
        plan.price_in_cents = plan.price_in_cents  / 10   # change  from $500/mo -> $50/mo
        db.session.add(plan)

    team_plans = Plan.query.filter(Plan.name=="team").all()
    for plan in team_plans:
        plan.price_in_cents = plan.price_in_cents / 6  # change from $1,500/mo -> $250/mo
        db.session.add(plan)
    db.session.commit()


def revision_91e81219d4ae_up():
    print_revision_function_name()
    db.session.execute('update plan set self_serve=true')
    db.session.execute('update plan set public=true')


def revision_91e81219d4ae_down():
    print_revision_function_name()
    db.session.execute('update plan set self_serve=null')
    db.session.execute('update plan set public=null')


def revision_fa3692965b28_up():
    print_revision_function_name()
    unattached_accounts = Account.query.filter(Account.stripe_customer_id==None).all()
    for account in unattached_accounts:
        stripe_customer = Account.create_stripe_customer(stripe_livemode=False)
        account.stripe_customer_id = stripe_customer['id']
        account.stripe_livemode = False
        db.session.add(account)
        current_app.logger.info(f"Attached {account.stripe_customer_id} to account {account.id}")
    db.session.commit()


def revision_fa3692965b28_down():
    print_revision_function_name()
