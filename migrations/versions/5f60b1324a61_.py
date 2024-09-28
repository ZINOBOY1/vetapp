"""empty message

Revision ID: 5f60b1324a61
Revises: caae9aa1ead8
Create Date: 2024-09-12 05:47:07.696850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f60b1324a61'
down_revision = 'caae9aa1ead8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Enum('pending', 'paid', 'failed'), server_default='pending', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###
