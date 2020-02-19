from dataclasses import dataclass
import uuid
import datetime as dt

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class TimestampMixin(object):
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


@dataclass
class Plan(TimestampMixin, db.Model):
    id: str
    name: str
    price_in_cents: int
    max_subjects_per_experiment: int
    max_active_experiments: int

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(), nullable=False, index=True)
    price_in_cents = db.Column(db.Integer(), nullable=False)
    max_subjects_per_experiment = db.Column(db.Integer(), nullable=False)
    max_active_experiments = db.Column(db.Integer(), nullable=False)


@dataclass
class Account(TimestampMixin, db.Model):
    plan: Plan

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('plan.id'), nullable=False)

    plan = db.relationship('Plan', backref='accounts', lazy="joined")

    @classmethod
    def create(cls, plan=None):
        plan = plan or Plan.query.filter(Plan.price_in_cents==0).first()
        account = cls(plan=plan)
        return account


# Should have roles for admin, logger
@dataclass
class Role(TimestampMixin, db.Model):
    id: str
    name: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(length=16), unique=True, index=True, nullable=False)


@dataclass
class Token(TimestampMixin, db.Model):
    id: str
    value: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('role.id'), nullable=False)
    value = db.Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)

    role = db.relationship('Role', lazy='joined')
    account = db.relationship('Account', lazy='joined')


@dataclass
class User(TimestampMixin, db.Model):
    id: str
    tokens: Token
    email: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'))

    email = db.Column(db.String(length=128), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=128), nullable=False)

    tokens = db.relationship('Token', lazy='joined', backref='user', cascade='delete')
    account = db.relationship('Account', lazy='joined', backref=db.backref('users', lazy='dynamic'))
    experiments = db.relationship('Experiment', lazy='dynamic', backref="user", cascade='delete')

    def __hash__(self):
        return hash(str(self.id))

    def set_password_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create(cls, email, password, account, token):
        user = cls(email=email, account=account)
        user.set_password_hash(password)
        user.tokens.append(token)
        token.account = account
        db.session.add(user)
        db.session.add(token)
        db.session.flush()
        return user


@dataclass
class Experiment(TimestampMixin, db.Model):
    id: str
    user_id: str
    name: str
    full: bool
    subjects_counter: int
    active: bool
    last_activated_at: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(length=64), index=True)

    subjects_counter = db.Column(db.Integer(), nullable=False, default=0)
    active = db.Column(db.Boolean(), nullable=False, index=True)
    last_activated_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'name'), )

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
            db.session.add_all(active_experiments)
        self.active = True
        self.last_activated_at = dt.datetime.now()
        db.session.add(self)
        db.session.flush()

    def deactivate(self):
        self.active = False
        db.session.add(self)
        db.session.flush()


class Subject(TimestampMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False)
    name = db.Column(db.String(length=64), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint('account_id', 'name'), )

    account = db.relationship('Account', backref=db.backref('subjects', lazy='dynamic'))


class Cohort(TimestampMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiment.id'), nullable=False)
    name = db.Column(db.String(length=64), nullable=False, index=True)

    experiment = db.relationship('Experiment', backref='cohorts')

    __table_args__ = (db.UniqueConstraint('experiment_id', 'name'), )


@dataclass
class Exposure(TimestampMixin, db.Model):
    id: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cohort_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cohort.id'), nullable=False)
    subject_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subject.id'), nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiment.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('subject_id', 'experiment_id'), )

    cohort = db.relationship('Cohort', backref=db.backref('exposures', lazy='dynamic'))
    subject = db.relationship('Subject', backref=db.backref('exposures', lazy='dynamic'))
    experiment = db.relationship('Experiment', backref=db.backref('exposures', lazy='dynamic'))
    conversion = db.relationship('Conversion', backref=db.backref('exposure', uselist=False), uselist=False)

    def __hash__(self):
        return hash(str(self.id))


class Conversion(TimestampMixin, db.Model):
    id: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exposure_id = db.Column(UUID(as_uuid=True), db.ForeignKey('exposure.id'), nullable=False, unique=True)
    value = db.Column(db.Float())
