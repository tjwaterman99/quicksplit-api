import datetime as dt

from flask import request, g, abort, current_app, make_response, json
from flask_restful import Api, Resource
from sqlalchemy.dialects.postgresql import insert

from app.models import (
    db, Account, User, Token, Experiment, Subject, Conversion, Exposure, Role,
    Cohort, Scope
)
from app.services import ExperimentResultCalculator

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


def protected(roles=None):
    roles = roles or ['admin']
    def decorator(function):
        def wrapper(*args, **kwargs):
            if current_app and g.user is None:
                abort(403)
            elif not any([g.user.has_role(role) for role in roles]):
                abort(403)
            else:
                return function(*args, **kwargs)
        return wrapper
    return decorator


def load_user():
    token_value = request.headers.get('Authorization')
    if token_value:
        token = Token.query.filter(Token.value==token_value).first()
        if token:
            g.user = token.user
            g.token = token
        else:
            g.user = None
            g.token = None
    else:
        g.user = None
        g.token = None


class IndexResource(Resource):
    def get(self):
        return {'healthy': True}


class UserResource(Resource):

    @protected()
    def get(self):
        return g.user

    def post(self):
        email = request.json['email']
        password = request.json['password']
        account = Account.create()
        user = User.create(email=email, password=password, account=account)
        return user


class LoginResource(Resource):

    def post(self):
        email = request.json['email']
        password = request.json['password']
        user = User.query.filter(User.email==email).first()
        if user.check_password(password):
            return user
        else:
            abort(403)


class ExperimentsResource(Resource):

    @protected()
    def get(self):
        return g.user.experiments.all()

    @protected()
    def post(self):
        name = request.json['name']
        experiment = Experiment(user=g.user, name=name)
        experiment.activate()
        db.session.add(experiment)
        return experiment


class ExperimentIdResource(Resource):

    @protected()
    def get(self, experiment_id):
        return g.user.experiments.filter(Experiment.id==experiment_id).first()


class ExposuresResource(Resource):

    # We might consider moving this business logic into a Exposure.create method
    @protected(roles=['admin', 'public'])
    def post(self):
        experiment_name = str(request.json['experiment'])
        subject_name = str(request.json['subject'])
        cohort_name = str(request.json['cohort'])

        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(422, "Experiment does not exist")

        if experiment.full:
            abort(422, "Experiment has reached max exposures limit")

        if not experiment.active:
            abort(422, "Experiment is not active")

        subject_insert = insert(Subject.__table__).values(
            account_id=g.user.account_id,
            name=subject_name,
            scope_id=g.token.scope.id
        ).on_conflict_do_update(
            constraint='subject_account_id_name_scope_id_key',
            set_={'updated_at': dt.datetime.now()}
        ).returning(Subject.id)

        cohort_insert = insert(Cohort.__table__).values(
            name=cohort_name,
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

    @protected(roles=['admin', 'public'])
    def post(self):
        experiment_name = str(request.json['experiment'])
        subject_name = str(request.json['subject'])

        # Allow users to not supply a value
        _value = request.json.get('value')
        if _value is not None:
            value = float(_value)
        else:
            value = None

        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(422, "Experiment does not exist")

        subject = Subject.query.filter(Subject.name==subject_name)\
                               .filter(Subject.account==experiment.user.account)\
                               .first()
        if not subject:
            abort(422, "Subject does not exist")
        exposure = Exposure.query.filter(Exposure.subject_id==subject.id)\
                                 .filter(Exposure.experiment_id==experiment.id)\
                                 .first()
        if not exposure:
            abort(422, "Subject does not have an exposure for that experiment yet")

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
    def get(self):
        experiment_name = request.json['experiment']

        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(404, "Experiment does not exist")
        if experiment.subjects_counter == 0:
            abort(400, "Experiment has not collected any data")
        erc = ExperimentResultCalculator(experiment)
        erc.load_exposures()

        anova = erc.anova()
        table = erc._summary_table()
        results = {
            'experiment': experiment.name,
            'table': table.reset_index().to_dict(orient='records'),
            'p-value': anova.f_pvalue,
            'significant': bool(anova.f_pvalue < 0.1),
            'subjects': int(anova.nobs)
        }
        return results


class ActivateResource(Resource):

    @protected()
    def post(self):
        experiment_name = request.json['experiment']
        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(404, "Experiment does not exist")
        experiment.activate()
        return experiment


class DeactivateResource(Resource):

    @protected()
    def post(self):
        experiment_name = request.json['experiment']
        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(404, "Experiment does not exist")
        experiment.deactivate()
        return experiment


class TokenRoleResource(Resource):

    @protected()
    def post(self, role_name, scope_name):
        role = Role.query.filter(Role.name==role_name).first()
        scope = Scope.query.filter(Scope.name==scope_name).first()
        if not role and not scope:
            abort(404)
        token = Token(role=role, scope=scope, user=g.user, account=g.user.account)
        db.session.add(token)
        db.session.flush()
        return token


class TokensResource(Resource):

    @protected()
    def get(self):
        return g.user.tokens


api.add_resource(IndexResource, '/')
api.add_resource(UserResource, '/user')
api.add_resource(ExperimentsResource, '/experiments')
api.add_resource(ExperimentIdResource, '/experiments/<experiment_id>')
api.add_resource(ExposuresResource, '/exposures')
api.add_resource(ConversionsResource, '/conversions')
api.add_resource(ResultsResource, '/results')
api.add_resource(LoginResource, '/login')
api.add_resource(ActivateResource, '/activate')
api.add_resource(DeactivateResource, '/deactivate')
api.add_resource(TokenRoleResource, '/tokens/<role_name>/<scope_name>')
api.add_resource(TokensResource, '/tokens')
