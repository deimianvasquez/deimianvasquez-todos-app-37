"""empty message

Revision ID: e6e3bc727490
Revises: 7efae2981f52
Create Date: 2024-12-04 23:07:17.707635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6e3bc727490'
down_revision = '7efae2981f52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('prueba', sa.String(length=80), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('prueba')

    # ### end Alembic commands ###
