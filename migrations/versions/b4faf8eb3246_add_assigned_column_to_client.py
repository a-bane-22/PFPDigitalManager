"""Add assigned column to Client

Revision ID: b4faf8eb3246
Revises: 0bfed65b6b47
Create Date: 2022-07-11 18:29:46.671419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4faf8eb3246'
down_revision = '0bfed65b6b47'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('client', sa.Column('assigned', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_client_assigned'), 'client', ['assigned'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_client_assigned'), table_name='client')
    op.drop_column('client', 'assigned')
    # ### end Alembic commands ###
