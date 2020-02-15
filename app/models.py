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

    account = db.relationship('Account', lazy="joined")


class Experiment(TimestampMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(), primary_key=True)
    name = db.Column(db.String(length=128), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'name'), )


class Subject(TimestampMixin, db.Model):
    subject_id = db.Column(db.String(length=64), primary_key=True)
    user_id = db.Column(UUID(), db.ForeignKey('user.id'), primary_key=True)


class Exposure(TimestampMixin, db.Model):
    experiment_id = db.Column(UUID(), primary_key=True)
    subject_id = db.Column(db.String(length=64), primary_key=True)
    user_id = db.Column(UUID(), primary_key=True)

    db.ForeignKeyConstraint(['subject_id', 'experiment_id', 'user_id'], ['subject.subject_id', 'experiment.id', 'user.id'])


class Conversion(TimestampMixin, db.Model):
    experiment_id = db.Column(UUID(), primary_key=True)
    subject_id = db.Column(db.String(length=64), primary_key=True)
    user_id = db.Column(UUID(), primary_key=True)

    db.ForeignKeyConstraint(['subject_id', 'experiment_id', 'user_id'], ['subject.subject_id', 'experiment.id', 'user.id'])
