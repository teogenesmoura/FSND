"""empty message

Revision ID: 7f49a551f219
Revises: 1e6bfc16559f
Create Date: 2020-07-14 17:30:33.454860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f49a551f219'
down_revision = '1e6bfc16559f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.DateTime(), nullable=True))
    op.drop_column('Show', 'show_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('show_time', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###