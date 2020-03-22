from pprint import pprint

from flask import current_app
from flask.cli import AppGroup
from click import argument, option
from rq import Worker, Connection
import redis

from app.models import db, ExposureRollup
from app.seeds import plans, roles, scopes, plan_schedules
from app.sql import exposures_summary
from migrations import data_migrations


seed = AppGroup(name="seed", help="Commands to seed the database")
rollup = AppGroup(name="rollup", help="Commands to run daily rollups")
worker = AppGroup(name="worker", help="Commands to manage the redis-queue worker")



@worker.command("run")
def run_worker():
    redis_url = current_app.config["REDIS_URL"]
    redis_connection = redis.from_url(redis_url)
    with Connection(redis_connection):
        worker = Worker(current_app.config["WORKER_QUEUES"])
        worker.work()


@seed.command()
def all():
    db.session.add_all(plan_schedules)
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


@rollup.command()
@argument('date')
def exposures(date):
    """
    Aggregate exposures for each experiment and environment, per day
    """

    query = exposures_summary.format(date=date)
    results = db.session.execute(query).fetchall()
    results_dict = list(dict(r) for r in results)
    db.session.bulk_insert_mappings(ExposureRollup, results_dict)
    if current_app.testing:
        db.session.flush()
        print("Not commiting during tests")
    else:
        db.session.commit()

    affected_users = set(d['user_id'] for d in results_dict)
    num_affected_users = len(affected_users)
    print(f"Ran rollup for {date}: {num_affected_users} affected users: {affected_users}")
