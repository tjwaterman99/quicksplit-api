"""Add payment_intent_id to orders

Revision ID: 8eb2ef7768cd
Revises: 152ffb0b8e11
Create Date: 2020-03-25 10:54:34.632055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8eb2ef7768cd'
down_revision = '152ffb0b8e11'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('payment_intent_id', sa.String(), nullable=False))
    op.add_column('order', sa.Column('succeeded', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_order_payment_intent_id'), 'order', ['payment_intent_id'], unique=False)
    op.create_index(op.f('ix_order_succeeded'), 'order', ['succeeded'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_order_succeeded'), table_name='order')
    op.drop_index(op.f('ix_order_payment_intent_id'), table_name='order')
    op.drop_column('order', 'succeeded')
    op.drop_column('order', 'payment_intent_id')
    # ### end Alembic commands ###