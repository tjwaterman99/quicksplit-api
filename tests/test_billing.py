import datetime as dt

from app.models import Account


def test_account_can_change_plans(db, user, paid_plan, free_plan):
    assert user.account.plan == free_plan

    user.account.change_plan(paid_plan)
    assert user.account.plan == paid_plan
    assert user.account.bill_at == dt.datetime.now().date() + paid_plan.schedule.interval

    user.account.change_plan(free_plan)
    assert user.account.plan == paid_plan
    assert user.account.bill_at == None
    assert user.account.downgrade_at == dt.datetime.now().date() + paid_plan.schedule.interval


def test_billable_accounts_get_loaded(db, user, paid_plan):
    user.account.change_plan(paid_plan)
    assert user.account in Account.load_billable_accounts(user.account.bill_at)


def test_downgradable_accounts_get_loaded(db, user, paid_plan, free_plan):
    user.account.change_plan(paid_plan)
    user.account.change_plan(free_plan)
    assert user.account in Account.load_downgradable_accounts(user.account.downgrade_at)
