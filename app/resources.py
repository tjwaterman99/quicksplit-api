from flask import request, g, abort, current_app, make_response, json
from flask_restful import Api, Resource
from sqlalchemy.dialects.postgresql import insert

from app.models import db, Account, User, Token, Experiment, Subject, Conversion, Exposure


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
    token = request.headers.get('Authorization')
    if token:
        # If they provide an invalid token, this will raise an error since
        # the query will return None, which doesn't have a .user attribute
        g.user = Token.query.get(token).user
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
        token = Token()
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
            return user.token
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
        experiment_name = request.json['experiment']
        subject_id = str(request.json['subject_id'])

        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(422, "Experiment does not exist")

        if experiment.full:
            abort(422, "Experiment has reached max exposures limit")

        subject_insert = insert(Subject.__table__).values(
            id=subject_id,
            user_id=g.user.id
        ).on_conflict_do_nothing().returning(Subject.id, Subject.user_id)
        exposure_insert = insert(Exposure.__table__).values(
            experiment_id=experiment.id,
            subject_id=subject_id,
            user_id=g.user.id
        ).on_conflict_do_nothing()

        inserted_subject = db.session.execute(subject_insert).fetchone()
        db.session.execute(exposure_insert)
        if inserted_subject:
            experiment.subjects_counter = Experiment.subjects_counter + 1
            db.session.add(experiment)
        db.session.commit()


class ConversionsResource(Resource):

    @protected
    def post(self):
        experiment_name = request.json['experiment']
        subject_id = str(request.json['subject_id'])

        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            abort(422, "Experiment does not exist")

        exposure = experiment.exposures.filter(Subject.id==subject_id).first()
        if not exposure:
            abort(422, "Subject does not have an exposure yet")

        conversion_insert = insert(Conversion.__table__).values(
            experiment_id=experiment.id,
            subject_id=subject_id,
            user_id=g.user.id
        ).on_conflict_do_nothing()
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


api.add_resource(IndexResource, '/')
api.add_resource(UserResource, '/user')
api.add_resource(ExperimentsResource, '/experiments')
api.add_resource(ExperimentIdResource, '/experiments/<experiment_id>')
api.add_resource(ExposuresResource, '/exposures')
api.add_resource(ConversionsResource, '/conversions')
api.add_resource(ResultsResource, '/results')
api.add_resource(LoginResource, '/login')
