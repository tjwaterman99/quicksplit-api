from flask.cli import AppGroup

from app.models import db
from app.seeds import plans, roles, scopes

seed = AppGroup(name="seed", help="Commands to seed the database")


@seed.command()
def all():
    db.session.add_all(plans)
    db.session.add_all(roles)
    db.session.add_all(scopes)
    db.session.commit()
