import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID


db = SQLAlchemy()


class TimestampMixin(object):
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class Account(TimestampMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    users = db.relationship('User', lazy="dynamic")


class User(TimestampMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.id'))

    account = db.relationship('Account', lazy='joined')
    experiments = db.relationship('Experiment', lazy='dynamic', backref="user", cascade='delete')
    subjects = db.relationship('Subject', lazy='dynamic', backref='user', cascade='delete')
    exposures = db.relationship('Exposure', lazy='dynamic', backref='user', cascade='delete',
                                primaryjoin='User.id==Exposure.user_id',
                                foreign_keys='Exposure.user_id')
    conversions = db.relationship('Conversion', lazy='dynamic', backref='user', cascade='delete',
                                  primaryjoin='User.id==Conversion.user_id',
                                  foreign_keys='Conversion.user_id')


# TODO: add relationship to subjects thru the exposures table
class Experiment(TimestampMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    name = db.Column(db.String(length=128), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'name'), )

    exposures = db.relationship('Exposure', lazy='dynamic', backref='experiment', cascade='delete')
    conversions = db.relationship('Conversion', lazy='dynamic', backref='experiment', cascade='delete')


# TODO: subjects should really be attached to an account, not just a user
class Subject(TimestampMixin, db.Model):
    id = db.Column(db.String(length=64), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)

    exposures = db.relationship('Exposure', lazy='dynamic', backref='subject', cascade='delete',
                                primaryjoin='and_(Subject.user_id==Exposure.user_id, Subject.id==Exposure.subject_id)',
                                foreign_keys='Exposure.subject_id')

    conversions = db.relationship('Conversion', lazy='dynamic', backref='subject', cascade='delete',
                                primaryjoin='and_(Subject.user_id==Conversion.user_id, Subject.id==Conversion.subject_id)',
                                foreign_keys='Conversion.subject_id')


class Exposure(TimestampMixin, db.Model):
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiment.id'), primary_key=True)
    subject_id = db.Column(db.String(length=64), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), primary_key=True)
    db.ForeignKeyConstraint(['subject_id', 'user_id'], ['subject.id', 'user.id'])


class Conversion(TimestampMixin, db.Model):
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiment.id'), primary_key=True)
    subject_id = db.Column(db.String(length=64), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), primary_key=True)
    db.ForeignKeyConstraint(['subject_id', 'user_id'], ['subject.id', 'user.id'])
