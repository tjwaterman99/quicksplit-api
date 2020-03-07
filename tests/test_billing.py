def test_account_can_change_plans(db, user, paid_plan, free_plan):
    user.account.change_plan(paid_plan)
    assert user.account.plan == paid_plan

    # We probably don't want to immediately change the plan if it's a downgrade
    # and instead schedule the plan to be downgraded
    user.account.change_plan(free_plan)
    assert user.account.plan == free_plan
