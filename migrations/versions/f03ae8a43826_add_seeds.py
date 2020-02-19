"""add seeds

Revision ID: f03ae8a43826
Revises: a89a9f029ff9
Create Date: 2020-02-19 00:31:45.707613

"""
from alembic import op
import sqlalchemy as sa
from dataclasses import asdict

from app.seeds import plans, roles, scopes
from app.models import Plan, Role, Scope


# revision identifiers, used by Alembic.
revision = 'f03ae8a43826'
down_revision = 'a89a9f029ff9'
branch_labels = None
depends_on = None


def upgrade():
    op.bulk_insert(Plan.__table__, [asdict(p) for p in plans])
    op.bulk_insert(Role.__table__, [asdict(r) for r in roles])
    op.bulk_insert(Scope.__table__, [asdict(s) for s in scopes])


def downgrade():
    op.execute('delete from plan where 1=1')
    op.execute('delete from role where 1=1')
    op.execute('delete from scope where 1=1')
