"""empty message

Revision ID: ef0a6b9a0090
Revises: 1c8be8db413a
Create Date: 2024-09-03 02:06:54.529954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef0a6b9a0090'
down_revision = '1c8be8db413a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Enum('active', 'disabled'), server_default='active', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###
