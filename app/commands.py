from flask.cli import AppGroup
from click import argument, option

from app.models import db
from app.seeds import plans, roles, scopes
from migrations import data_migrations

seed = AppGroup(name="seed", help="Commands to seed the database")


@seed.command()
def all():
    db.session.add_all(plans)
    db.session.add_all(roles)
    db.session.add_all(scopes)
    db.session.commit()


@seed.command()
@argument("_revision")
@option("--up", default=False, is_flag=True)
@option("--down", default=False, is_flag=True)
def revision(_revision, up, down):
    current_revision = db.session.execute('select * from alembic_version').fetchone()[0]
    if up and down:
        raise ValueError("Can not provide both --up and --down flags")
    if not up and not down:
        raise ValueError("Must provide on of --up and --down flags")

    if up:
        end = "up"
    else:
        end = "down"

    if current_revision != _revision:
        raise ValueError(f"Supplied revision '{_revision}' does not match current database revision {current_revision}")
    try:
        command = getattr(data_migrations, f"revision_{_revision}_{end}")
    except AttributeError:
        raise AttributeError(f"No migration command found for revision {_revision}_{end}")
    return command()
