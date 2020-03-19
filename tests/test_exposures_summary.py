import datetime as dt

from app.sql import exposures_summary
from app.commands import exposures as rollup_exposures
from app.models import ExposureRollup


def test_exposures_summary_sql(db, user, experiment, exposure, conversion):
    date = exposure.last_seen_at.date()
    query = exposures_summary.format(date=date)
    results = db.session.execute(query).fetchall()
    assert len(results) == 1
    data = dict(results[0])
    assert data['exposures'] == 1
    assert data['conversions'] == 1


def test_exposures_summary_sql_staging(db, user, experiment, exposure_staging):
    date = exposure_staging.last_seen_at.date()
    query = exposures_summary.format(date=date)
    results = db.session.execute(query).fetchall()
    assert len(results) == 1
    data = dict(results[0])
    assert data['exposures'] == 1
    assert data['conversions'] == 0


def test_rollup_command(app, db, user, experiment, exposure, conversion):
    user_id = str(user.id)
    date = str(exposure.last_seen_at.date())
    runner = app.test_cli_runner()
    result = runner.invoke(rollup_exposures, date)
    assert user_id in result.output
    assert "1 affected users" in result.output
    assert date in result.output


def test_summaries_exposures_get(db, client, user, exposures_rollup):
    # The route doesn't include the current day by default, so
    # we move the ned date forward 1 day to pick up the newly created data
    end_date = exposures_rollup.day + dt.timedelta(days=1)
    resp = client.get('/summaries/exposures', query_string={
        "end_date": end_date
    })
    assert resp.status_code == 200
    assert len(resp.json['data']) == 1
    assert resp.json['data'][0]['user_id'] == str(exposures_rollup.user_id)
