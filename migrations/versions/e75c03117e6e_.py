"""empty message

Revision ID: e75c03117e6e
Revises: 1e13c9dfc990
Create Date: 2018-07-12 22:51:24.535897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e75c03117e6e'
down_revision = '1e13c9dfc990'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=64), nullable=True),
    sa.Column('path', sa.Unicode(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=64), nullable=True),
    sa.Column('path', sa.Unicode(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('image')
    op.drop_table('file')
    # ### end Alembic commands ###
