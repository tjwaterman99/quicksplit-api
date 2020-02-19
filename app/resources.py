import datetime as dt

from flask import request, g, abort, current_app, make_response, json
from flask_restful import Api, Resource
from sqlalchemy.dialects.postgresql import insert

from app.models import db, Account, User, Token, Experiment, Subject, Conversion, Exposure, Role, Cohort


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


def protected(function):
    def wrapper(*args, **kwargs):
        if current_app and g.user is None:
            abort(403)
        else:
            return function(*args, **kwargs)
    return wrapper


def load_user():
    token_value = request.headers.get('Authorization')
    if token_value:
        token = Token.query.filter(Token.value==token_value).first()
        if token:
            g.user = token.user
        else:
            g.user = None
    else:
        g.user = None


class IndexResource(Resource):
    def get(self):
        return {'healthy': True}


class UserResource(Resource):

    @protected
    def get(self):
        return g.user

    def post(self):
        email = request.json['email']
        password = request.json['password']
        account = Account.create()
        role = Role.query.filter(Role.name=="admin").first()
        token = Token(role=role)
        user = User.create(email=email, password=password, account=account,
                           token=token)
        db.session.add(user)
        db.session.commit()
        return user


class LoginResource(Resource):

    def post(self):
        email = request.json['email']
        password = request.json['password']
        user = User.query.filter(User.email==email).first()
        if user.check_password(password):
            return user.tokens[0]
        else:
            abort(403)


class ExperimentsResource(Resource):

    @protected
    def get(self):
        return g.user.experiments.all()

    @protected
    def post(self):
        name = request.json['name']
        experiment = Experiment(user=g.user, name=name)
        experiment.activate()
        db.session.add(experiment)
        db.session.commit()
        return experiment


class ExperimentIdResource(Resource):

    @protected
    def get(self, experiment_id):
        return g.user.experiments.filter(Experiment.id==experiment_id).first()


class ExposuresResource(Resource):

    # We might consider moving this object into a Exposure.create method
    @protected
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
            name=subject_name
        ).on_conflict_do_update(
            constraint='subject_account_id_name_key',
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
            cohort_id=cohort_id
        ).on_conflict_do_nothing().returning(Exposure.id)

        exposure_id = db.session.execute(exposure_insert).fetchone()
        print(subject_id)
        if exposure_id:
            experiment.subjects_counter = Experiment.subjects_counter + 1
            db.session.add(experiment)
        db.session.commit()


class ConversionsResource(Resource):

    @protected
    def post(self):
        experiment_name = str(request.json['experiment'])
        subject_name = str(request.json['subject'])
        value = float(request.json['value']) or None

        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(422, "Experiment does not exist")

        exposure = experiment.exposures.filter(Subject.name==subject_name).first()
        if not exposure:
            abort(422, "Subject does not have an exposure yet")

        conversion_insert = insert(Conversion.__table__).values(
            exposure_id=exposure.id,
            value=value
        ).on_conflict_do_update(
            constraint='conversion_exposure_id_key',
            set_={'updated_at': dt.datetime.now()}
        )
        db.session.execute(conversion_insert)
        db.session.commit()


class ResultsResource(Resource):

    @protected
    def get(self):
        experiment_name = request.json['experiment']

        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(404, "Experiment does not exist")
        return experiment


class ActivateResource(Resource):

    @protected
    def post(self):
        experiment_name = request.json['experiment']
        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(404, "Experiment does not exist")
        experiment.activate()
        db.session.commit()
        return experiment


class DeactivateResource(Resource):

    @protected
    def post(self):
        experiment_name = request.json['experiment']
        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(404, "Experiment does not exist")
        experiment.deactivate()
        db.session.commit()
        return experiment


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
