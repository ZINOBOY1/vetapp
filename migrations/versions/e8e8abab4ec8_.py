"""empty message

Revision ID: e8e8abab4ec8
Revises: 71cc8fe46a39
Create Date: 2024-09-10 22:34:16.513649

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e8e8abab4ec8'
down_revision = '71cc8fe46a39'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.alter_column('quantity',
               existing_type=mysql.INTEGER(display_width=11),
               type_=sa.String(length=255),
               existing_nullable=False)

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('order_total',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('order_total',
               existing_type=sa.String(length=255),
               type_=mysql.DECIMAL(precision=10, scale=2),
               existing_nullable=False)

    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.alter_column('quantity',
               existing_type=sa.String(length=255),
               type_=mysql.INTEGER(display_width=11),
               existing_nullable=False)

    # ### end Alembic commands ###
