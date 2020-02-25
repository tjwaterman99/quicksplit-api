"""Add indexes on timestamp fields

Revision ID: afa833a13e7e
Revises: d72f8a7404ec
Create Date: 2020-02-25 03:56:56.517868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afa833a13e7e'
down_revision = 'd72f8a7404ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_account_created_at'), 'account', ['created_at'], unique=False)
    op.create_index(op.f('ix_account_updated_at'), 'account', ['updated_at'], unique=False)
    op.create_index(op.f('ix_cohort_created_at'), 'cohort', ['created_at'], unique=False)
    op.create_index(op.f('ix_cohort_updated_at'), 'cohort', ['updated_at'], unique=False)
    op.create_index(op.f('ix_conversion_created_at'), 'conversion', ['created_at'], unique=False)
    op.create_index(op.f('ix_conversion_last_seen_at'), 'conversion', ['last_seen_at'], unique=False)
    op.create_index(op.f('ix_conversion_updated_at'), 'conversion', ['updated_at'], unique=False)
    op.create_index(op.f('ix_experiment_created_at'), 'experiment', ['created_at'], unique=False)
    op.create_index(op.f('ix_experiment_updated_at'), 'experiment', ['updated_at'], unique=False)
    op.create_index(op.f('ix_exposure_created_at'), 'exposure', ['created_at'], unique=False)
    op.create_index(op.f('ix_exposure_last_seen_at'), 'exposure', ['last_seen_at'], unique=False)
    op.create_index(op.f('ix_exposure_updated_at'), 'exposure', ['updated_at'], unique=False)
    op.create_index(op.f('ix_plan_created_at'), 'plan', ['created_at'], unique=False)
    op.create_index(op.f('ix_plan_updated_at'), 'plan', ['updated_at'], unique=False)
    op.create_index(op.f('ix_role_created_at'), 'role', ['created_at'], unique=False)
    op.create_index(op.f('ix_role_updated_at'), 'role', ['updated_at'], unique=False)
    op.create_index(op.f('ix_scope_created_at'), 'scope', ['created_at'], unique=False)
    op.create_index(op.f('ix_scope_updated_at'), 'scope', ['updated_at'], unique=False)
    op.create_index(op.f('ix_subject_created_at'), 'subject', ['created_at'], unique=False)
    op.create_index(op.f('ix_subject_updated_at'), 'subject', ['updated_at'], unique=False)
    op.create_index(op.f('ix_token_created_at'), 'token', ['created_at'], unique=False)
    op.create_index(op.f('ix_token_updated_at'), 'token', ['updated_at'], unique=False)
    op.create_index(op.f('ix_user_created_at'), 'user', ['created_at'], unique=False)
    op.create_index(op.f('ix_user_updated_at'), 'user', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_updated_at'), table_name='user')
    op.drop_index(op.f('ix_user_created_at'), table_name='user')
    op.drop_index(op.f('ix_token_updated_at'), table_name='token')
    op.drop_index(op.f('ix_token_created_at'), table_name='token')
    op.drop_index(op.f('ix_subject_updated_at'), table_name='subject')
    op.drop_index(op.f('ix_subject_created_at'), table_name='subject')
    op.drop_index(op.f('ix_scope_updated_at'), table_name='scope')
    op.drop_index(op.f('ix_scope_created_at'), table_name='scope')
    op.drop_index(op.f('ix_role_updated_at'), table_name='role')
    op.drop_index(op.f('ix_role_created_at'), table_name='role')
    op.drop_index(op.f('ix_plan_updated_at'), table_name='plan')
    op.drop_index(op.f('ix_plan_created_at'), table_name='plan')
    op.drop_index(op.f('ix_exposure_updated_at'), table_name='exposure')
    op.drop_index(op.f('ix_exposure_last_seen_at'), table_name='exposure')
    op.drop_index(op.f('ix_exposure_created_at'), table_name='exposure')
    op.drop_index(op.f('ix_experiment_updated_at'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_created_at'), table_name='experiment')
    op.drop_index(op.f('ix_conversion_updated_at'), table_name='conversion')
    op.drop_index(op.f('ix_conversion_last_seen_at'), table_name='conversion')
    op.drop_index(op.f('ix_conversion_created_at'), table_name='conversion')
    op.drop_index(op.f('ix_cohort_updated_at'), table_name='cohort')
    op.drop_index(op.f('ix_cohort_created_at'), table_name='cohort')
    op.drop_index(op.f('ix_account_updated_at'), table_name='account')
    op.drop_index(op.f('ix_account_created_at'), table_name='account')
    # ### end Alembic commands ###
