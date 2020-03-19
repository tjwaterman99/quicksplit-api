"""Add exposures rollup

Revision ID: 2d3d0de55ad2
Revises: 37618de9724e
Create Date: 2020-03-19 03:09:43.581995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2d3d0de55ad2'
down_revision = '37618de9724e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exposure_rollup',
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('day', sa.Date(), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('experiment_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('experiment_name', sa.String(), nullable=False),
    sa.Column('scope_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('exposures', sa.Integer(), nullable=False),
    sa.Column('conversions', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('day', 'experiment_id', 'scope_id')
    )
    op.create_index(op.f('ix_exposure_rollup_account_id'), 'exposure_rollup', ['account_id'], unique=False)
    op.create_index(op.f('ix_exposure_rollup_created_at'), 'exposure_rollup', ['created_at'], unique=False)
    op.create_index(op.f('ix_exposure_rollup_day'), 'exposure_rollup', ['day'], unique=False)
    op.create_index(op.f('ix_exposure_rollup_experiment_id'), 'exposure_rollup', ['experiment_id'], unique=False)
    op.create_index(op.f('ix_exposure_rollup_scope_id'), 'exposure_rollup', ['scope_id'], unique=False)
    op.create_index(op.f('ix_exposure_rollup_updated_at'), 'exposure_rollup', ['updated_at'], unique=False)
    op.create_index(op.f('ix_exposure_rollup_user_id'), 'exposure_rollup', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_exposure_rollup_user_id'), table_name='exposure_rollup')
    op.drop_index(op.f('ix_exposure_rollup_updated_at'), table_name='exposure_rollup')
    op.drop_index(op.f('ix_exposure_rollup_scope_id'), table_name='exposure_rollup')
    op.drop_index(op.f('ix_exposure_rollup_experiment_id'), table_name='exposure_rollup')
    op.drop_index(op.f('ix_exposure_rollup_day'), table_name='exposure_rollup')
    op.drop_index(op.f('ix_exposure_rollup_created_at'), table_name='exposure_rollup')
    op.drop_index(op.f('ix_exposure_rollup_account_id'), table_name='exposure_rollup')
    op.drop_table('exposure_rollup')
    # ### end Alembic commands ###
