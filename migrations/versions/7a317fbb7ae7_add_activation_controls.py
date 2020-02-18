"""Add activation controls

Revision ID: 7a317fbb7ae7
Revises: 50a9a16519b9
Create Date: 2020-02-18 19:41:45.432220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a317fbb7ae7'
down_revision = '50a9a16519b9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('experiment', sa.Column('active', sa.Boolean(), nullable=True))
    op.add_column('experiment', sa.Column('last_activated_at', sa.DateTime(), nullable=True))

    op.execute('update experiment set active=false')
    op.execute('update experiment set last_activated_at=now()')

    op.create_index(op.f('ix_experiment_active'), 'experiment', ['active'], unique=False)
    op.create_index(op.f('ix_experiment_last_activated_at'), 'experiment', ['last_activated_at'], unique=False)

    op.execute('alter table experiment alter column active set not null')
    op.execute('alter table experiment alter column last_activated_at set not null')

    op.add_column('plan', sa.Column('max_active_experiments', sa.Integer(), nullable=True))
    op.execute('update plan set max_active_experiments = 3 where price_in_cents=0')
    op.execute('update plan set max_active_experiments = 10 where price_in_cents=100*50')
    op.execute('update plan set max_active_experiments = 25 where price_in_cents=100*250')
    op.execute('update plan set max_active_experiments = 25 where price_in_cents=100*1000')
    op.execute('alter table plan alter column max_active_experiments set not null')

def downgrade():
    op.drop_index(op.f('ix_experiment_last_activated_at'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_active'), table_name='experiment')
    op.drop_column('experiment', 'last_activated_at')
    op.drop_column('experiment', 'active')
