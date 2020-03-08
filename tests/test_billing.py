import datetime as dt
from unittest.mock import patch

from app.models import Account, Order


def test_account_can_change_plans(db, user, paid_plan, free_plan):
    assert user.account.plan == free_plan

    user.account.change_plan(paid_plan)
    assert user.account.plan == paid_plan
    assert user.account.bill_at == dt.datetime.now().date() + paid_plan.schedule.interval

    user.account.change_plan(free_plan)
    assert user.account.plan == paid_plan
    assert user.account.bill_at == None
    assert user.account.downgrade_at == dt.datetime.now().date() + paid_plan.schedule.interval


def test_immediate_downgrade_changes_plan(db, user, paid_plan, free_plan):
    user.account.change_plan(paid_plan)
    user.account.downgrade(free_plan, immediate=True)
    assert user.account.plan == free_plan
    assert user.account.bill_at == None
    assert user.account.downgrade_at == None


def test_billable_accounts_get_loaded(db, user, paid_plan):
    user.account.change_plan(paid_plan)
    assert user.account in Account.load_billable_accounts(user.account.bill_at)


def test_downgradable_accounts_get_loaded(db, user, paid_plan, free_plan):
    user.account.change_plan(paid_plan)
    user.account.change_plan(free_plan)
    assert user.account in Account.load_downgradable_accounts(user.account.downgrade_at)


def test_free_plan_has_no_billing_credits(db, user):
    assert user.account.billing_credits == 0


def test_free_plan_has_no_days_until_next_bill(db, user):
    assert user.account.days_until_next_bill == None


def test_upgrading_creates_an_order(db, user, paid_plan):
    user.account.change_plan(paid_plan)
    first_order = user.account.orders.first()
    assert first_order.amount == paid_plan.price_in_cents
    assert first_order.plan == paid_plan


def test_days_until_next_bill(db, user, paid_plan):
    user.account.upgrade(paid_plan)
    assert user.account.days_until_next_bill == paid_plan.schedule.interval.days

    # Set billing to 20 days in the future
    intermediate_billing_date = dt.datetime.now().date() + dt.timedelta(days=20)
    user.account.bill_at = intermediate_billing_date
    assert user.account.days_until_next_bill == 20

    # Set billing to 0 days in the future
    last_billing_date = dt.datetime.now().date() + dt.timedelta(days=0)
    user.account.bill_at = last_billing_date
    assert user.account.days_until_next_bill == 0


def test_billing_credits(db, user, paid_plan):
    user.account.upgrade(paid_plan)
    assert user.account.billing_credits == paid_plan.price_in_cents

    # Set billing to 20 days in the future, so they haven't used 2/3 of their plan
    intermediate_billing_date = dt.datetime.now().date() + dt.timedelta(days=20)
    user.account.bill_at = intermediate_billing_date
    assert user.account.billing_credits == paid_plan.price_in_cents * 2/3

    # Set billing to 0 days in the future, so they've used 100% of their plan
    last_billing_date = dt.datetime.now().date() + dt.timedelta(days=0)
    user.account.bill_at = last_billing_date
    assert user.account.billing_credits == 0


# TODO: test these plan type changes
# Free to free
# Paid to free
# Paid to paid
# Same paid to same paid
# Same paid to different billing cycle duration
#
