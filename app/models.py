from typing import Dict, List
from dataclasses import dataclass, asdict
import uuid
import datetime as dt

from flask import g, request, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID, insert, JSONB, INTERVAL
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

from app.encoders import CustomJSONEncoder

db = SQLAlchemy(engine_options={'json_serializer': CustomJSONEncoder().encode})

from app.exceptions import ApiException
from app.services import ExperimentResultCalculator
from app.proxies import worker, mailer


class AsyncWriterMixin(object):
    """
    Helper class for writing models in async workers. Ensures that various
    methods get called even when there is no flask request context, including
    commiting the database session.
    """

    @classmethod
    def create_async(cls, *create_args, **create_kwargs):
        if not hasattr(cls, 'create'):
            raise ApiException(500, f"Can't save model {cls.__name__} asynchronously.")
        return worker.enqueue(cls._create_async, args=create_args, kwargs=create_kwargs)

    @classmethod
    def _create_async(cls, *create_args, **create_kwargs):
        obj = cls.create(*create_args, **create_kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj


class TimestampMixin(object):

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)


@dataclass(init=False)
class EventTrackerMixin(object):

    last_exposure_at: str
    last_conversion_at: str

    @declared_attr
    def last_exposure_id_staging(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('exposure.id', name='experiment_last_exposure_id_staging_fkey'), index=True)

    @declared_attr
    def last_exposure_id_production(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('exposure.id', name='experiment_last_exposure_id_production_fkey'), index=True)

    @declared_attr
    def last_conversion_id_staging(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('conversion.id', name='experiment_last_conversion_id_staging_fkey'), index=True)

    @declared_attr
    def last_conversion_id_production(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('conversion.id', name='experiment_last_conversion_id_production_fkey'), index=True)

    @declared_attr
    def last_exposure_staging(cls):
        return db.relationship("Exposure", foreign_keys=[cls.last_exposure_id_staging], lazy="joined")

    @declared_attr
    def last_exposure_production(cls):
        return db.relationship("Exposure", foreign_keys=[cls.last_exposure_id_production], lazy="joined")

    @declared_attr
    def last_conversion_staging(cls):
        return db.relationship("Conversion", foreign_keys=[cls.last_conversion_id_staging], lazy="joined")

    @declared_attr
    def last_conversion_production(cls):
        return db.relationship("Conversion", foreign_keys=[cls.last_conversion_id_production], lazy="joined")

    @property
    def last_exposure(self):
        if not request or g.token.scope.name == 'production':
            return self.last_exposure_production
        else:
            return self.last_exposure_staging

    @property
    def last_conversion(self):
        if not request or g.token.scope.name == 'production':
            return self.last_conversion_production
        else:
            return self.last_conversion_staging

    @property
    def last_exposure_at(self):
        if self.last_exposure:
            return self.last_exposure.last_seen_at

    @property
    def last_conversion_at(self):
        if self.last_conversion:
            return self.last_conversion.last_seen_at


@dataclass
class Session(TimestampMixin, db.Model):
    id: str
    user: "User"
    created_at: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, index=True)

    user = db.relationship("User", lazy="joined", uselist=False, backref=db.backref("sessions", lazy="dynamic"))

    @classmethod
    def create(cls, email, password):
        user = User.query.filter(User.email==email).first()
        if not user:
            raise ApiException(404, "Account not found")
        if not user.check_password(password):
            raise ApiException(403, "Invalid password")
        else:
            session = cls(user=user)
            db.session.add(session)
            db.session.flush()
            return session


@dataclass
class Contact(AsyncWriterMixin, TimestampMixin, db.Model):
    id: str
    email: str
    message: str
    subject: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), index=True)
    email = db.Column(db.String(), nullable=False, index=True)
    subject = db.Column(db.String(), nullable=False)
    message = db.Column(db.String(), nullable=False)

    user = db.relationship("User", lazy="joined", uselist=False)

    @classmethod
    def create(cls, email, subject, message):
        if 'token' in g:
            user = g.token.user
        else:
            user = None
        contact = cls(user=None, email=email, subject=subject, message=message)
        db.session.add(contact)
        db.session.flush()
        mailer.send_text_email(to=email, subject=subject, content=message)
        return contact


@dataclass
class Event(TimestampMixin, db.Model):
    id: str
    name: str
    user_id: str
    data: dict

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(), nullable=False, index=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), index=True)
    data = db.Column(JSONB())

    user = db.relationship("User", backref=db.backref("events", lazy="dynamic"))


@dataclass
class PlanSchedule(TimestampMixin, db.Model):
    name: str
    interval: dt.timedelta
    interval_days: int

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(), nullable=False, index=True, unique=True)
    interval = db.Column(INTERVAL, nullable=False, index=True, unique=True)

    def __repr__(self):
        return f"<PlanSchedule {self.name}>"

    @property
    def interval_days(self):
        return self.interval.days

    __tablename__ = "plan_schedule"


@dataclass
class Plan(TimestampMixin, db.Model):

    ranks = {
        'free': 0,
        'developer': 1,
        'team': 2,
        'custom': 3
    }

    id: str
    name: str
    price_in_cents: int
    max_subjects_per_experiment: int
    max_active_experiments: int
    self_serve: bool
    public: bool
    schedule: PlanSchedule
    schedule_name: str
    rank: int

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(), nullable=False, index=True)
    price_in_cents = db.Column(db.Integer(), nullable=False)
    max_subjects_per_experiment = db.Column(db.Integer(), nullable=False)
    max_active_experiments = db.Column(db.Integer(), nullable=False)
    schedule_id = db.Column(UUID(as_uuid=True), db.ForeignKey('plan_schedule.id'), index=True)
    public = db.Column(db.Boolean(), default=False)
    self_serve = db.Column(db.Boolean(), default=False)

    schedule =  db.relationship('PlanSchedule', backref="plan", uselist=False)

    @property
    def schedule_name(self):
        if self.schedule:
            return self.schedule.name

    @property
    def rank(self):
        return self.ranks[self.name]

    def __repr__(self):
        return f"<Plan {self.name} schedule={self.schedule}>"

    def __lt__(self, other):
        if self.rank < other.rank:
            return True
        else:
            return self.price_in_cents < other.price_in_cents

    def __eq__(self, other):
        return self.rank == other.rank and self.price_in_cents == other.price_in_cents


@dataclass
class Order(TimestampMixin, db.Model):
    id: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('plan.id'), nullable=False, index=True)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False, index=True)
    amount = db.Column(db.Integer(), nullable=False, index=True)
    payment_intent_id = db.Column(db.String(), nullable=False, index=True)
    succeeded = db.Column(db.Boolean(), nullable=False, index=True)

    account = db.relationship('Account', backref=db.backref('orders', lazy="dynamic"), lazy="joined")
    plan = db.relationship('Plan', backref=db.backref('orders', lazy="dynamic"), lazy="joined")

    @classmethod
    def create(cls, plan, account, amount):
        if account.payment_methods == []:
            raise ApiException(403, "No payment methods found on account.")
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=plan.price_in_cents,
                currency="usd",
                payment_method=account.payment_methods[0].stripe_payment_method_id,
                customer=account.stripe_customer_id,
                off_session=True,
                confirm=True,
                description=f"Order for {account} on plan {plan}",
                api_key=account.stripe_secret_key)
            succeeded = True
            payment_intent_id = payment_intent.id
        except stripe.error.CardError as e:
            succeeded = False
            payment_intent_id = err.payment_intent_id
        order = cls(plan=plan, account=account, amount=amount,
                    succeeded=succeeded, payment_intent_id=payment_intent_id)
        db.session.add(order)
        db.session.flush()
        return order

    def __repr__(self):
        return f"<Order ${self.amount / 100} ({self.account.id}, {self.plan.name} [{self.plan.schedule.interval}])>"


@dataclass
class PlanChange(TimestampMixin, db.Model):
    id: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False, index=True)
    plan_change_from_id = db.Column(UUID(as_uuid=True), db.ForeignKey('plan.id'), nullable=False, index=True)
    plan_change_to_id = db.Column(UUID(as_uuid=True), db.ForeignKey('plan.id'), nullable=False, index=True)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('order.id'), nullable=True, index=True)

    __tablename__ = "plan_change"

    plan_change_from = db.relationship('Plan', foreign_keys=[plan_change_from_id], lazy="joined")
    plan_change_to = db.relationship('Plan', foreign_keys=[plan_change_to_id], lazy="joined")
    account = db.relationship('Account', backref=db.backref('plan_changes', lazy="dynamic"), lazy="joined")
    order = db.relationship('Order', backref=db.backref('plan_change', lazy="joined", uselist=False), lazy="joined")

    @classmethod
    def create(cls, account, plan_change_from, plan_change_to, order=None):
        plan_change = cls(account=account, plan_change_from=plan_change_from,
                          plan_change_to=plan_change_to, order=order)
        db.session.add(plan_change)
        db.session.flush()
        return plan_change

    def __repr__(self):
        return f"<PlanChange [{self.plan_change_from.name} to {self.plan_change_to.name}]>"


@dataclass
class PaymentMethod(TimestampMixin, db.Model):
    id: str
    stripe_payment_method_id: str
    stripe_data: dict

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False, index=True)
    stripe_payment_method_id = db.Column(db.String(), nullable=False)
    stripe_data = db.Column(JSONB())

    account = db.relationship("Account", backref=db.backref("payment_methods", lazy="joined"), lazy="joined")

    @classmethod
    def create(cls, account, stripe_payment_method_id, stripe_data=None):
        payment_method = cls(
            account=account,
            stripe_payment_method_id=stripe_payment_method_id,
            stripe_data=stripe_data
        )
        db.session.add(payment_method)
        db.session.flush()
        return payment_method


@dataclass(init=False)
class Account(TimestampMixin, db.Model):
    plan: Plan
    id: str
    payment_methods: List[PaymentMethod]
    downgrade_plan: Plan
    downgrade_at: str
    bill_at: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('plan.id'), nullable=False, index=True)
    downgrade_plan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('plan.id'), nullable=True, index=True)
    downgrade_at = db.Column(db.Date(), nullable=True)
    bill_at = db.Column(db.Date(), nullable=True)
    stripe_customer_id = db.Column(db.String())
    stripe_livemode = db.Column(db.Boolean(), default=False)

    plan = db.relationship('Plan', backref='accounts', lazy="joined", foreign_keys=[plan_id])
    downgrade_plan = db.relationship('Plan', lazy="joined", foreign_keys=[downgrade_plan_id])

    def __repr__(self):
        return f"<Account {self.id}>"

    @classmethod
    def create_stripe_customer(cls, stripe_livemode=False):
        if stripe_livemode:
            api_key = current_app.config['STRIPE_PRODUCTION_SECRET_KEY']
        else:
            api_key = current_app.config['STRIPE_TEST_SECRET_KEY']
        return stripe.Customer.create(api_key=api_key)

    @classmethod
    def create(cls, plan=None, stripe_customer_id=None, stripe_livemode=False):
        plan = plan or Plan.query.filter(Plan.price_in_cents==0).first()
        stripe_livemode = stripe_livemode or current_app.env == "production"
        if not stripe_customer_id:
            stripe_customer = cls.create_stripe_customer(stripe_livemode=stripe_livemode)
            stripe_customer_id = stripe_customer['id']
        account = cls(plan=plan, stripe_customer_id=stripe_customer_id, stripe_livemode=stripe_livemode)
        db.session.add(account)
        db.session.flush()
        return account

    @classmethod
    def load_billable_accounts(cls, date):
        return cls.query.filter(cls.bill_at==date).all()

    @classmethod
    def load_downgradable_accounts(cls, date):
        return cls.query.filter(cls.downgrade_at==date).all()

    @property
    def stripe_secret_key(self):
        if self.stripe_livemode:
            return current_app.config['STRIPE_PRODUCTION_SECRET_KEY']
        else:
            return current_app.config['STRIPE_TEST_SECRET_KEY']

    def create_stripe_setup_intent(self):
        return stripe.SetupIntent.create(
            api_key=self.stripe_secret_key,
            customer=self.stripe_customer_id
        )

    def change_plan(self, plan):
        current_plan = self.plan
        # This could be moved into it's own method "unschedule downgrade"
        if plan == self.plan:
            self.bill_at = self.downgrade_at
            self.downgrade_at = None
            self.downgrade_plan = None
            order = None
            db.session.add(self)
            db.session.flush()
        elif plan > self.plan:
            order = self.upgrade(plan)
        else:
            self.downgrade(plan)
            order = None
        return PlanChange.create(account=self, plan_change_from=current_plan,
                                 plan_change_to=plan, order=order)

    def charge(self, amount, plan):
        return Order.create(plan=plan, account=self, amount=amount)

    @property
    def days_until_next_bill(self):
        bill_or_downgrade_day = self.bill_at or self.downgrade_at
        if not bill_or_downgrade_day:
            return None
        return (bill_or_downgrade_day - dt.datetime.now().date()).days

    @property
    def billing_credits(self):
        if not self.days_until_next_bill:
            return 0
        return self.plan.price_in_cents * self.days_until_next_bill / self.plan.schedule.interval.days

    def upgrade(self, plan):
        order = self.charge(plan.price_in_cents - self.billing_credits, plan=plan)
        self.plan = plan
        self.bill_at = dt.datetime.now().date() + self.plan.schedule.interval
        self.downgrade_at = None
        self.downgrade_plan = None
        db.session.add(self)
        db.session.flush()
        return order

    def downgrade(self, plan, immediate=False):
        if immediate is True:
            self.plan = plan
            self.downgrade_at = None
            self.downgrade_plan = None
        else:
            self.downgrade_plan = plan
            self.downgrade_at = self.bill_at or self.downgrade_at
        if plan.price_in_cents == 0:
            self.bill_at = None
        else:
            self.bill_at = self.bill_at or dt.datetime.now() + plan.schedule.interval
        db.session.add(self)
        db.session.flush()


@dataclass
class Role(TimestampMixin, db.Model):
    id: str
    name: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(length=16), index=True, nullable=False, unique=True)


@dataclass
class Scope(TimestampMixin, db.Model):
    id: str
    name: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(length=16), index=True, nullable=False, unique=True)


@dataclass
class Token(TimestampMixin, db.Model):
    id: str
    value: str
    environment: str
    private: bool

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, index=True)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False, index=True)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('role.id'), nullable=False, index=True)
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False, index=True)
    value = db.Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)

    account = db.relationship('Account', lazy='joined')
    role = db.relationship('Role', lazy='joined')
    scope = db.relationship('Scope', lazy="joined")

    @property
    def private(self):
        return self.role.name in ['admin']

    @property
    def environment(self):
        return self.scope.name


@dataclass
class User(TimestampMixin, db.Model):
    id: str
    tokens: Token
    email: str
    admin_token: Token
    account: Account

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), index=True)

    email = db.Column(db.String(length=128), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=128), nullable=False)

    tokens = db.relationship('Token', lazy='joined', backref='user', cascade='delete')
    account = db.relationship('Account', lazy='joined', backref=db.backref('users', lazy='dynamic'))
    experiments = db.relationship('Experiment', lazy='dynamic', backref="user", cascade='all')

    def __hash__(self):
        return hash(str(self.id))

    def set_password_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_tokens(self):
        for role in Role.query.all():
            for scope in Scope.query.all():
                token = Token(scope=scope, role=role, user=self, account=self.account)
                db.session.add(token)

    @property
    def admin_token(self):
        for token in self.tokens:
            if token.role.name == "admin" and token.scope.name == "production":
                return token

    @property
    def admin_token_staging(self):
        for token in self.tokens:
            if token.role.name == "admin" and token.scope.name == "staging":
                return token

    @classmethod
    def create(cls, email, password, account=None):
        account = account or Account.create()
        user = cls(email=email, account=account)
        try:
            with db.session.no_autoflush:
                user.set_password_hash(password)
                user.set_tokens()
            db.session.add(user)
            db.session.flush()
        except IntegrityError as exc:
            raise ApiException(403, "User with that email already exists.")
        return user

    @classmethod
    def login(cls, email, password):
        user = User.query.filter(User.email==email).first()
        if not user:
            raise ApiException(404, "Could not find that account.")
        elif not user.check_password(password):
            raise ApiException(403, "Invalid password.")
        else:
            return user

    def has_role(self, role: str):
        for token in self.tokens:
            if role == token.role.name:
                return True
        else:
            return False


@dataclass
class Experiment(EventTrackerMixin, TimestampMixin, db.Model):
    name: str
    full: bool
    subjects_counter: int
    active: bool
    last_activated_at: str
    id: str
    user_id: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, index=True)
    name = db.Column(db.String(length=64), index=True)

    subjects_counter_production = db.Column(db.Integer(), nullable=False, default=0)
    subjects_counter_staging = db.Column(db.Integer(), nullable=False, default=0)
    active = db.Column(db.Boolean(), nullable=False, index=True, default=False)
    last_activated_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True, default=func.now())  # We should allow this to be nullable

    __table_args__ = (db.UniqueConstraint('user_id', 'name'), )

    @classmethod
    def create(cls, name, user):
        experiment = cls(user=user, name=name)
        try:
            db.session.add(experiment)
            db.session.flush()
        except IntegrityError:
            raise ApiException(403, "Experiment with that name already exists")
        experiment.activate()
        return experiment

    @property
    def subjects_counter(self):
        if not request or g.token.scope.name == 'production':
            return self.subjects_counter_production
        else:
            return self.subjects_counter_staging

    @property
    def full(self):
        return self.subjects_counter >= self.user.account.plan.max_subjects_per_experiment

    def activate(self):
        if self.active:
            return
        active_experiments = self.user.experiments.filter(Experiment.active==True)\
                                                  .order_by(Experiment.last_activated_at.desc())\
                                                  .all()
        if len(active_experiments) >= self.user.account.plan.max_active_experiments:
            active_experiments[0].deactivate()
        self.active = True
        self.last_activated_at = dt.datetime.now()
        db.session.add(self)
        db.session.flush()

    def deactivate(self):
        self.active = False
        db.session.add(self)
        db.session.flush()


@dataclass(init=False)
class ExperimentResult(TimestampMixin, db.Model):
    id: str
    experiment_id: str
    version: str
    fields: Dict
    ran_at: str
    ran: bool
    experiment_name: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiment.id'), nullable=False, index=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, index=True)
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False, index=True)
    version = db.Column(db.String(10))
    fields = db.Column(JSONB())
    ran_at = db.Column(db.DateTime(timezone=True), index=True)

    experiment = db.relationship('Experiment', lazy='joined', backref=db.backref('results', lazy='dynamic'))
    user = db.relationship('User', lazy="joined", backref=db.backref('experiment_results', lazy="dynamic"))
    scope = db.relationship('Scope', lazy='joined')

    @classmethod
    def create(cls, experiment, scope):
        if experiment.subjects_counter == 0:
            raise ApiException(400, f"Experiment {experiment.name} has no subjects yet. Can't create a report!")
        experiment_result = cls(experiment=experiment, scope=scope, user=experiment.user)
        db.session.add(experiment_result)
        db.session.flush()
        return experiment_result

    @property
    def experiment_name(self):
        return self.experiment.name

    @property
    def ran(self):
        return self.ran_at is not None

    def run(self):
        erc = ExperimentResultCalculator(experiment=self.experiment, scope=self.scope)
        erc.run()
        self.fields = asdict(erc)
        self.version = erc.version
        self.ran_at = dt.datetime.now()
        db.session.add(self)
        db.session.flush()
        return self


@dataclass
class Subject(EventTrackerMixin, TimestampMixin, db.Model):
    subject_id: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False, index=True)
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False, index=True)
    name = db.Column(db.String(length=64), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint('account_id', 'name', 'scope_id'), )

    account = db.relationship('Account', backref=db.backref('subjects', lazy='dynamic'))
    scope = db.relationship('Scope', lazy='joined')

    @property
    def subject_id(self):
        return self.name


@dataclass
class Cohort(EventTrackerMixin, TimestampMixin, db.Model):
    name: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiment.id'), nullable=False, index=True)
    name = db.Column(db.String(length=64), nullable=False, index=True)

    experiment = db.relationship('Experiment', backref='cohorts')

    __table_args__ = (db.UniqueConstraint('experiment_id', 'name'), )


@dataclass
class Exposure(TimestampMixin, db.Model):
    id: str
    cohort: Cohort
    subject: Subject
    experiment: Experiment
    scope: Scope
    last_seen_at: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cohort_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cohort.id'), nullable=False, index=True)
    subject_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subject.id'), nullable=False, index=True)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiment.id'), nullable=False, index=True)
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False, index=True)
    last_seen_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint('subject_id', 'experiment_id', 'scope_id'), )

    cohort = db.relationship('Cohort', backref=db.backref('exposures', lazy='dynamic'), foreign_keys=[cohort_id], lazy="joined")
    subject = db.relationship('Subject', backref=db.backref('exposures', lazy='dynamic'), foreign_keys=[subject_id], lazy="joined")
    experiment = db.relationship('Experiment', backref=db.backref('exposures', lazy='dynamic'), lazy="joined", foreign_keys=[experiment_id])
    scope = db.relationship('Scope', lazy='joined')
    conversion = db.relationship('Conversion', backref=db.backref('exposure', uselist=False, lazy="joined"), uselist=False, lazy="joined")

    def __hash__(self):
        return hash(str(self.id))

    @classmethod
    def create(cls, subject_name, cohort_name, experiment_name):
        # Note that using this method requires a request context since we depend on
        # the user being pulled from `g`. If we move this to a worker node
        # we'll have to pass in a user_id to refetch the user.
        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            raise ApiException(404, "Experiment does not exist")

        if experiment.full:
            raise ApiException(422, "Experiment has reached max exposures limit")

        if not experiment.active:
            raise ApiException(422, "Experiment is not active")

        subject_insert = insert(Subject.__table__).values(
            account_id=g.user.account_id,
            name=subject_name,
            scope_id=g.token.scope.id
        ).on_conflict_do_update(
            constraint='subject_account_id_name_scope_id_key',
            set_={'updated_at': func.now()}
        ).returning(Subject.id)
        subject_id = db.session.execute(subject_insert).fetchone()[0]

        cohort_insert = insert(Cohort.__table__).values(
            name=cohort_name,
            experiment_id=experiment.id,
        ).on_conflict_do_update(
            constraint='cohort_experiment_id_name_key',
            set_={'updated_at': func.now()}
        ).returning(Cohort.id)
        cohort_id = db.session.execute(cohort_insert).fetchone()[0]

        exposure_insert = insert(Exposure.__table__).values(
            experiment_id=experiment.id,
            subject_id=subject_id,
            cohort_id=cohort_id,
            scope_id=g.token.scope.id
        ).on_conflict_do_update(
            constraint="exposure_subject_id_experiment_id_scope_id_key",
            set_={'last_seen_at': func.now()}
        ).returning(Exposure.id, Exposure.last_seen_at)

        # Note that the exposure_insert hasn't actually been commited yet, so
        # the update to `last_seen_at` here will be correct, while the ORMs
        # Exposure.query.get(exposure_id) will not produce the latest
        # `last_seen_at` value.
        exposure_id, last_seen_at = db.session.execute(exposure_insert).fetchone()

        subject = Subject.query.get(subject_id)
        cohort = Cohort.query.get(cohort_id)
        exposure = Exposure.query.get(exposure_id)
        production = g.token.scope.name == 'production'

        if production:
            experiment.last_exposure_production = exposure
            subject.last_exposure_production = exposure
            cohort.last_exposure_production = exposure
            if exposure.created_at == last_seen_at:
                experiment.subjects_counter_production = Experiment.subjects_counter_production + 1
        else:
            experiment.last_exposure_staging = exposure
            subject.last_exposure_staging = exposure
            cohort.last_exposure_staging = exposure
            if exposure.created_at == last_seen_at:
                experiment.subjects_counter_staging = Experiment.subjects_counter_staging + 1

        db.session.add_all([experiment, subject, cohort])
        db.session.flush()
        return exposure


@dataclass
class Conversion(TimestampMixin, db.Model):
    id: str
    last_seen_at: str
    scope: Scope
    value: float

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exposure_id = db.Column(UUID(as_uuid=True), db.ForeignKey('exposure.id'), nullable=False, index=True)
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False, index=True)
    value = db.Column(db.Float())
    last_seen_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint('exposure_id', 'scope_id'), )

    scope = db.relationship('Scope', lazy='joined')

    @classmethod
    def create(cls, subject_name, experiment_name, value=None):
        # Note that using this function requires a request context since we depend on
        # the user being pulled from `g`. If we move this to a worker node
        # we'll have to pass in a user_id to refetch the user.
        experiment = g.user.experiments.filter(Experiment.name==experiment_name).first()
        if not experiment:
            raise ApiException(404, "Experiment does not exist")

        subject = Subject.query.filter(Subject.name==subject_name)\
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
            set_={'last_seen_at': dt.datetime.now()}
        ).returning(Conversion.id)
        conversion_id = db.session.execute(conversion_insert).fetchall()[0]

        conversion = Conversion.query.get(conversion_id)
        production = g.token.scope.name == 'production'

        if production:
            experiment.last_conversion_production = conversion
            subject.last_conversion_production = conversion
            conversion.exposure.cohort.last_conversion_production = conversion
        else:
            experiment.last_conversion_staging = conversion
            subject.last_conversion_staging = conversion
            conversion.exposure.cohort.last_conversion_staging = conversion

        db.session.add_all([experiment, subject, conversion])
        db.session.flush()
        return conversion


@dataclass
class ExposureRollup(TimestampMixin, db.Model):
    day: str
    user_id: str
    account_id: str
    experiment_id: str
    experiment_name: str
    scope_id: str
    exposures: int
    conversions: int

    # No foreign keys in case a dependant object gets deleted before the job
    # can finish
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day = db.Column(db.Date(), nullable=False, index=True)
    user_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    account_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    experiment_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    experiment_name = db.Column(db.String(), nullable=False)
    scope_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    exposures = db.Column(db.Integer(), nullable=False)
    conversions = db.Column(db.Integer(), nullable=False)

    __table_args__ = (db.UniqueConstraint('day', 'experiment_id', 'scope_id'), )

    user = db.relationship("User", primaryjoin="User.id==ExposureRollup.user_id", foreign_keys=[user_id], backref=db.backref('exposures_rollups', lazy="dynamic"))
