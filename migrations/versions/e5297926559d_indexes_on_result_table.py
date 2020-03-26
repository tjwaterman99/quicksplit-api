"""Indexes on result table

Revision ID: e5297926559d
Revises: 8eb2ef7768cd
Create Date: 2020-03-26 13:56:34.731339

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5297926559d'
down_revision = '8eb2ef7768cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_experiment_result_experiment_id'), 'experiment_result', ['experiment_id'], unique=False)
    op.create_index(op.f('ix_experiment_result_scope_id'), 'experiment_result', ['scope_id'], unique=False)
    op.create_index(op.f('ix_experiment_result_user_id'), 'experiment_result', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_experiment_result_user_id'), table_name='experiment_result')
    op.drop_index(op.f('ix_experiment_result_scope_id'), table_name='experiment_result')
    op.drop_index(op.f('ix_experiment_result_experiment_id'), table_name='experiment_result')
    # ### end Alembic commands ###
