"""add seeds

Revision ID: f03ae8a43826
Revises: 733b77e99e43
Create Date: 2020-02-19 00:31:45.707613

"""
from alembic import op
import sqlalchemy as sa
from dataclasses import asdict

from app.seeds import plans, roles
from app.models import Plan, Role


# revision identifiers, used by Alembic.
revision = 'f03ae8a43826'
down_revision = '733b77e99e43'
branch_labels = None
depends_on = None


def upgrade():
    op.bulk_insert(Plan.__table__, [asdict(p) for p in plans])
    op.bulk_insert(Role.__table__, [asdict(r) for r in roles])


def downgrade():
    op.execute('delete from plan where 1=1')
    op.execute('delete from role where 1=1')
