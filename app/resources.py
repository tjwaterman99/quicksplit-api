import datetime as dt

from flask import request, g, current_app, make_response, json, session
from flask_restful import Api, Resource
from funcy import decorator

from app.models import (
    db, Account, User, Token, Experiment, Subject, Conversion, Exposure, Role,
    Cohort, Scope, Event, Plan, Contact, PaymentMethod, Session
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
    if not request.json:
        raise ApiException(422, f"Missing required parameters: {list(required)}")
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


class SessionsResource(Resource):
    @params('email', 'password')
    def post(self, email, password):
        sess = Session.create(email=email, password=password)
        session['id'] = str(sess.id)
        return sess

    def delete(self):
        sess = Session.query.get(session['id'])
        if not sess:
            raise ApiException(404, "Session not found")
        db.session.delete(sess)
        db.session.flush()
        session.clear()
        return sess


class UserResource(Resource):

    @protected()
    def get(self):
        return g.user

    @params('email', 'password')
    def post(self, email, password):
        user = User.create(email, password)
        db.session.flush()
        sess = Session.create(email=email, password=password)
        session['id'] = str(sess.id)
        return user


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
        return Experiment.create(name=name, user=g.user)


class ExposuresResource(Resource):

    # We might consider moving this business logic into a Exposure.create method
    @protected(['admin', 'public'])
    @params('experiment', 'subject', 'cohort')
    def post(self, experiment, subject, cohort):
        subject = str(subject)
        cohort = str(cohort)
        experiment = str(experiment)
        return Exposure.create(subject_name=subject, cohort_name=cohort, experiment_name=experiment)


class ConversionsResource(Resource):

    @protected(['admin', 'public'])
    @params('experiment', 'subject', value=None)
    def post(self, experiment, subject, value):
        subject = str(subject)
        experiment = str(experiment)
        value = float(value) if value is not None else value
        return Conversion.create(subject_name=subject, experiment_name=experiment, value=value)


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

    # TODO: we should have a service object for pulling recent events
    @protected()
    def get(self):
        re = recent_events.format(user_id=g.user.id, scope_name=g.token.scope.name)
        return [dict(r) for r in db.session.execute(re).fetchall()]


class EventsResource(Resource):

    @params("name", user_id=None, data=None)
    def post(self, name, user_id, data):
        event = Event(name=name, user_id=user_id, data=data)
        db.session.add(event)
        db.session.flush()
        return event


class PlansResource(Resource):

    def get(self):
        return Plan.query.filter(Plan.public==True).all()


class ContactsResource(Resource):

    @params("email", "subject", "message")
    def post(self, email, subject, message):
        missing_fields = []
        if not email:
            missing_fields.append("Email")
        if not subject:
            missing_fields.append("Subject")
        if not message:
            missing_fields.append("Message")

        if missing_fields:
            raise ApiException(401, f"Please include the following information: {missing_fields}")
        return Contact.create(email=email, subject=subject, message=message)


class AccountPaymentSetupResource(Resource):

    @protected()
    def get(self):
        return g.user.account.create_stripe_setup_intent()


class StripeWebhooksResource(Resource):

    def payment_method_attached(self):
        stripe_customer_id = request.json['data']['object']['customer']
        account = Account.query.filter(Account.stripe_customer_id==stripe_customer_id).first()
        if not account:
            raise ApiException(404, f"No account with stripe customer id {stripe_customer_id} found.")
        stripe_payment_method_id = request.json['data']['object']['id']
        return PaymentMethod.create(account=account, stripe_data=request.json, stripe_payment_method_id=stripe_payment_method_id)

    def post(self):
        current_app.logger.info(f"Received stripe webhook {request.json['type']} ({request.json['id']})")
        if request.json['type'] == "payment_method.attached":
            return self.payment_method_attached()
        else:
            logger.info(f"No handling for stripe webhook type: {request.json['type']} ({request.json['id']})")


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
api.add_resource(EventsResource, '/events')
api.add_resource(PlansResource, '/plans')
api.add_resource(ContactsResource, '/contacts')
api.add_resource(AccountPaymentSetupResource, '/account/payment-setup')
api.add_resource(StripeWebhooksResource, '/webhooks/stripe')
api.add_resource(SessionsResource, '/sessions')
