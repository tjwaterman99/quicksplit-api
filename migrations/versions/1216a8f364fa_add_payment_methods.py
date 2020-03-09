"""add payment methods

Revision ID: 1216a8f364fa
Revises: fa3692965b28
Create Date: 2020-03-09 21:48:22.805209

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1216a8f364fa'
down_revision = 'fa3692965b28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_method',
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('stripe_payment_method_id', sa.String(), nullable=False),
    sa.Column('stripe_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_method_created_at'), 'payment_method', ['created_at'], unique=False)
    op.create_index(op.f('ix_payment_method_updated_at'), 'payment_method', ['updated_at'], unique=False)
    op.create_index(op.f('ix_account_stripe_customer_id'), 'account', ['stripe_customer_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payment_method_updated_at'), table_name='payment_method')
    op.drop_index(op.f('ix_payment_method_created_at'), table_name='payment_method')
    # op.drop_index(op.f('ix_account_stripe_customer_id'), table_name='account')
    op.drop_table('payment_method')
    # ### end Alembic commands ###
