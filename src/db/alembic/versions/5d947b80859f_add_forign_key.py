"""add forign key

Revision ID: 5d947b80859f
Revises: da2a58f49f4a
Create Date: 2020-08-11 16:01:44.055032

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5d947b80859f'
down_revision = 'da2a58f49f4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('members', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'members', 'team', ['team_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'members', type_='foreignkey')
    op.drop_column('members', 'team_id')
    # ### end Alembic commands ###
