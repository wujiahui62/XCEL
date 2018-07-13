"""empty message

Revision ID: f907de7584ac
Revises: 9547bbe43cb4
Create Date: 2018-07-13 10:02:33.326863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f907de7584ac'
down_revision = '9547bbe43cb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_image_table',
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event_image_table')
    # ### end Alembic commands ###
