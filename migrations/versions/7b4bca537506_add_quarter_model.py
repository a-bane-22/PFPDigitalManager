"""Add Quarter model

Revision ID: 7b4bca537506
Revises: 85767b7468be
Create Date: 2022-07-28 13:39:09.741464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b4bca537506'
down_revision = '85767b7468be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quarter',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_date', sa.Date(), nullable=True),
    sa.Column('to_date', sa.Date(), nullable=True),
    sa.Column('aum', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quarter_from_date'), 'quarter', ['from_date'], unique=False)
    op.create_index(op.f('ix_quarter_to_date'), 'quarter', ['to_date'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_quarter_to_date'), table_name='quarter')
    op.drop_index(op.f('ix_quarter_from_date'), table_name='quarter')
    op.drop_table('quarter')
    # ### end Alembic commands ###