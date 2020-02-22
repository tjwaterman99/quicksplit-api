import datetime as dt

from flask import request, g, abort, current_app, make_response, json
from flask_restful import Api, Resource, abort
from funcy import decorator
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import literal_column

from app.models import (
    db, Account, User, Token, Experiment, Subject, Conversion, Exposure, Role,
    Cohort, Scope
)
from app.services import ExperimentResultCalculator
from app.sql import recent_events
from app.exceptions import ApiException


api = Api()


@api.representation('application/json')
def output_json(data, code, headers=None):
    result = {
        'data': data,
        'status_code': code
    }
    resp = make_response(json.dumps(result, indent=2), code)
    resp.headers.extend(headers or {})
    return resp


@decorator
def protected(call, roles=['admin']):
    if current_app and g.user is None:
        raise ApiException(403, "Permission denied. Please log in to access this resource.")
    elif not any([g.user.has_role(role) for role in roles]):
        raise ApiException(403, message="Permission denied. User does not have access to this resource.")
    else:
        return call._func(*call._args, **call._kwargs)


@decorator
def params(call, *required, **optional):
    json = {**optional, **request.json}
    missing_params = [param for param in required if param not in json]
    unexpected_params = [param for param in json if (param not in required and param not in optional.keys())]
    if any(missing_params):
        raise ApiException(422, f"Missing required parameters: {missing_params}")
    if any(unexpected_params):
        raise ApiException(422, f"Received invalid parameters: {unexpected_params}")
    return call._func(*call._args, **json)


class IndexResource(Resource):
    def get(self):
        return {'healthy': True}


class UserResource(Resource):

    @protected()
    def get(self):
        return g.user

    @params('email', 'password')
    def post(self, email, password):
        return User.create(email, password)


class LoginResource(Resource):

    @params('email', 'password')
    def post(self, email, password):
        return User.login(email, password)


class ExperimentsResource(Resource):

    @protected()
    def get(self):
        return g.user.experiments.all()

    @protected()
    @params('name')
    def post(self, name):
        return Experiment.create(name)


class ExposuresResource(Resource):

    # We might consider moving this business logic into a Exposure.create method
    @protected(['admin', 'public'])
    @params('experiment', 'subject', 'cohort')
    def post(self, experiment, subject, cohort):
        subject = str(subject)
        cohort = str(cohort)
        experiment = str(experiment)

        experiment = g.user.experiments.filter(Experiment.name==experiment).first()
        if not experiment:
            raise ApiException(404, "Experiment does not exist")

        if experiment.full:
            raise ApiException(422, "Experiment has reached max exposures limit")

        if not experiment.active:
            raise ApiException(422, "Experiment is not active")

        subject_insert = insert(Subject.__table__).values(
            account_id=g.user.account_id,
            name=subject,
            scope_id=g.token.scope.id
        ).on_conflict_do_update(
            constraint='subject_account_id_name_scope_id_key',
            set_={'updated_at': dt.datetime.now()}
        ).returning(Subject.id)

        cohort_insert = insert(Cohort.__table__).values(
            name=cohort,
            experiment_id=experiment.id,
        ).on_conflict_do_update(
            constraint='cohort_experiment_id_name_key',
            set_={'updated_at': dt.datetime.now()}
        ).returning(Cohort.id)

        subject_id = db.session.execute(subject_insert).fetchone()[0]
        cohort_id = db.session.execute(cohort_insert).fetchone()[0]

        exposure_insert = insert(Exposure.__table__).values(
            experiment_id=experiment.id,
            subject_id=subject_id,
            cohort_id=cohort_id,
            scope_id=g.token.scope.id
        ).on_conflict_do_nothing().returning(Exposure.id)

        exposure_id = db.session.execute(exposure_insert).fetchone()
        if exposure_id:
            if g.token.scope.name == 'production':
                experiment.subjects_counter_production = Experiment.subjects_counter_production + 1
            elif g.token.scope.name == 'staging':
                experiment.subjects_counter_staging = Experiment.subjects_counter_staging + 1
            else:
                current_app.logger.error(f"Unexpected scope name {scope.name}")
            db.session.add(experiment)
        db.session.flush()


class ConversionsResource(Resource):

    @protected(['admin', 'public'])
    @params('experiment', 'subject', value=None)
    def post(self, experiment, subject, value):
        subject = str(subject)
        experiment = str(experiment)
        experiment = g.user.experiments.filter(Experiment.name==experiment).first()
        if not experiment:
            raise ApiException(404, "Experiment does not exist")

        subject = Subject.query.filter(Subject.name==subject)\
                               .filter(Subject.account==experiment.user.account)\
                               .first()
        if not subject:
            raise ApiException(404, "Subject does not exist")
        exposure = Exposure.query.filter(Exposure.subject_id==subject.id)\
                                 .filter(Exposure.experiment_id==experiment.id)\
                                 .first()
        if not exposure:
            raise ApiException(404, "Subject does not have an exposure for that experiment yet")

        conversion_insert = insert(Conversion.__table__).values(
            exposure_id=exposure.id,
            value=value,
            scope_id=g.token.scope.id
        ).on_conflict_do_update(
            constraint='conversion_exposure_id_scope_id_key',
            set_={'updated_at': dt.datetime.now()}
        )
        db.session.execute(conversion_insert)


class ResultsResource(Resource):

    @protected()
    @params('experiment')
    def get(self, experiment):
        experiment = g.user.experiments.filter(Experiment.name==experiment).first()
        if not experiment:
            raise ApiException(404, "Experiment does not exist")
        if experiment.subjects_counter == 0:
            raise ApiException(400, "Experiment has not collected any data")
        erc = ExperimentResultCalculator(experiment, scope_name=g.token.scope.name)
        erc.run()
        return erc


class ActivateResource(Resource):

    @protected()
    @params('experiment')
    def post(self, experiment):
        experiment = g.user.experiments.filter(Experiment.name==experiment).first()
        if not experiment:
            raise ApiException(404, "Experiment does not exist")
        experiment.activate()
        return experiment


class DeactivateResource(Resource):

    @protected()
    @params('experiment')
    def post(self, experiment):
        experiment = g.user.experiments.filter(Experiment.name==experiment).first()
        if not experiment:
            raise ApiException(404, "Experiment does not exist")
        experiment.deactivate()
        return experiment


class TokensResource(Resource):

    @protected()
    def get(self):
        return g.user.tokens


class RecentResource(Resource):

    # TODO: create a `last_seen_at` field for cohort, subject, exposure, conversions
    # and use that over the `updated_at` field
    # TODO: we should have a service object for pulling recent events
    @protected()
    def get(self):
        re = recent_events.format(user_id=g.user.id, scope_name=g.token.scope.name)
        return [dict(r) for r in db.session.execute(re).fetchall()]


api.add_resource(IndexResource, '/')
api.add_resource(UserResource, '/user')
api.add_resource(ExperimentsResource, '/experiments')
api.add_resource(ExposuresResource, '/exposures')
api.add_resource(ConversionsResource, '/conversions')
api.add_resource(ResultsResource, '/results')
api.add_resource(LoginResource, '/login')
api.add_resource(ActivateResource, '/activate')
api.add_resource(DeactivateResource, '/deactivate')
api.add_resource(TokensResource, '/tokens')
api.add_resource(RecentResource, '/recent')
