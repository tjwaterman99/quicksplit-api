from dataclasses import dataclass
import uuid
import datetime as dt

from flask import g, request, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID, insert
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app.exceptions import ApiException

db = SQLAlchemy()


class TimestampMixin(object):

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


@dataclass(init=False)
class EventTrackerMixin(object):

    last_exposure_at: str
    last_conversion_at: str

    @declared_attr
    def last_exposure_id_staging(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('exposure.id', name='experiment_last_exposure_id_staging_fkey'))

    @declared_attr
    def last_exposure_id_production(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('exposure.id', name='experiment_last_exposure_id_production_fkey'))

    @declared_attr
    def last_conversion_id_staging(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('conversion.id', name='experiment_last_conversion_id_staging_fkey'))

    @declared_attr
    def last_conversion_id_production(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('conversion.id', name='experiment_last_conversion_id_production_fkey'))

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
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('role.id'), nullable=False)
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False)
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

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'))

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
    def create(cls, email, password):
        account = Account.create()
        user = cls(email=email, account=account)
        try:
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
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(length=64), index=True)

    subjects_counter_production = db.Column(db.Integer(), nullable=False, default=0)
    subjects_counter_staging = db.Column(db.Integer(), nullable=False, default=0)
    active = db.Column(db.Boolean(), nullable=False, index=True, default=False)
    last_activated_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True, default=func.now())  # We should allow this to be nullable

    __table_args__ = (db.UniqueConstraint('user_id', 'name'), )

    @classmethod
    def create(cls, name):
        experiment = cls(user=g.user, name=name)
        try:
            experiment.activate()
        except IntegrityError:
            raise ApiException(403, "Experiment with that name already exists")
        db.session.add(experiment)
        db.session.flush()
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


class Subject(EventTrackerMixin, TimestampMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'), nullable=False)
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False)
    name = db.Column(db.String(length=64), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint('account_id', 'name', 'scope_id'), )

    account = db.relationship('Account', backref=db.backref('subjects', lazy='dynamic'))
    scope = db.relationship('Scope', lazy='joined')


class Cohort(EventTrackerMixin, TimestampMixin, db.Model):
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
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False)
    last_seen_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

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
        ).returning(Exposure.id)
        exposure_id = db.session.execute(exposure_insert).fetchone()

        subject = Subject.query.get(subject_id)
        cohort = Cohort.query.get(cohort_id)
        exposure = Exposure.query.get(exposure_id)
        production = g.token.scope.name == 'production'

        if production:
            experiment.last_exposure_production = exposure
            subject.last_exposure_production = exposure
            cohort.last_exposure_production = exposure
            if exposure.created_at != exposure.updated_at:
                experiment.subjects_counter_production = Experiment.subjects_counter_production + 1
            else:
                experiment.subjects_counter_production = 1
        else:
            experiment.last_exposure_staging = exposure
            subject.last_exposure_staging = exposure
            cohort.last_exposure_staging = exposure
            if exposure.created_at != exposure.updated_at:
                experiment.subjects_counter_staging = Experiment.subjects_counter_staging + 1
            else:
                experiment.subjects_counter_staging = 1

        db.session.add_all([experiment, subject, cohort])
        db.session.flush()
        return exposure


@dataclass
class Conversion(TimestampMixin, db.Model):
    id: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exposure_id = db.Column(UUID(as_uuid=True), db.ForeignKey('exposure.id'), nullable=False)
    scope_id = db.Column(UUID(as_uuid=True), db.ForeignKey('scope.id'), nullable=False)
    value = db.Column(db.Float())
    last_seen_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (db.UniqueConstraint('exposure_id', 'scope_id'), )

    scope = db.relationship('Scope', lazy='joined')

    @classmethod
    def create(cls, subject_name, experiment_name, value=None):
        # Note that using this method requires a request context since we depend on
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

        # This needs to return the conversion id, which can then be inserted
        # into the cohort, subject, and experiment tables as the `last_conversion_id_{scope}`
        # field
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
