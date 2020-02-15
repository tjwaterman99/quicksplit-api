from app.models import Account, User


def test_user_create(db):
    account = Account()
    user = User(account=account)
    db.session.add(user)
    db.session.commit()
    assert User.query.first() == user
    assert Account.query.first() == account
    assert user in account.users.all()
    assert account == user.account


def test_user_delete(user, db):
    db.session.delete(user)
    db.session.commit()
    assert User.query.get(user.id) == None
