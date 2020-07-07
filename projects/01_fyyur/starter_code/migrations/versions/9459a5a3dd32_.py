"""empty message

Revision ID: 9459a5a3dd32
Revises: 9e173d40e119
Create Date: 2020-07-03 20:09:54.471083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9459a5a3dd32'
down_revision = '9e173d40e119'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('image_link', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'image_link')
    # ### end Alembic commands ###