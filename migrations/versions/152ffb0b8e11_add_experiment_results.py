"""Add experiment results

Revision ID: 152ffb0b8e11
Revises: 2d3d0de55ad2
Create Date: 2020-03-20 18:37:47.740892

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '152ffb0b8e11'
down_revision = '2d3d0de55ad2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('experiment_result',
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('experiment_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('scope_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('version', sa.String(length=10), nullable=True),
    sa.Column('fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('ran_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['experiment_id'], ['experiment.id'], ),
    sa.ForeignKeyConstraint(['scope_id'], ['scope.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiment_result_created_at'), 'experiment_result', ['created_at'], unique=False)
    op.create_index(op.f('ix_experiment_result_ran_at'), 'experiment_result', ['ran_at'], unique=False)
    op.create_index(op.f('ix_experiment_result_updated_at'), 'experiment_result', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_experiment_result_updated_at'), table_name='experiment_result')
    op.drop_index(op.f('ix_experiment_result_ran_at'), table_name='experiment_result')
    op.drop_index(op.f('ix_experiment_result_created_at'), table_name='experiment_result')
    op.drop_table('experiment_result')
    # ### end Alembic commands ###
