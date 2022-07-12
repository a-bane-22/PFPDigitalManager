"""Add User, ClientGroup, Client, Account, and Custodian

Revision ID: 0bfed65b6b47
Revises: 
Create Date: 2022-07-11 17:59:04.244225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bfed65b6b47'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('custodian',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_custodian_name'), 'custodian', ['name'], unique=False)
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_group_name'), 'group', ['name'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=32), nullable=True),
    sa.Column('last_name', sa.String(length=32), nullable=True),
    sa.Column('middle_name', sa.String(length=32), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('cell_phone', sa.String(length=10), nullable=True),
    sa.Column('work_phone', sa.String(length=10), nullable=True),
    sa.Column('home_phone', sa.String(length=10), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_client_cell_phone'), 'client', ['cell_phone'], unique=False)
    op.create_index(op.f('ix_client_dob'), 'client', ['dob'], unique=False)
    op.create_index(op.f('ix_client_email'), 'client', ['email'], unique=True)
    op.create_index(op.f('ix_client_first_name'), 'client', ['first_name'], unique=False)
    op.create_index(op.f('ix_client_home_phone'), 'client', ['home_phone'], unique=False)
    op.create_index(op.f('ix_client_last_name'), 'client', ['last_name'], unique=False)
    op.create_index(op.f('ix_client_middle_name'), 'client', ['middle_name'], unique=False)
    op.create_index(op.f('ix_client_work_phone'), 'client', ['work_phone'], unique=False)
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_number', sa.String(length=32), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.Column('billable', sa.Boolean(), nullable=True),
    sa.Column('discretionary', sa.Boolean(), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('custodian_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.ForeignKeyConstraint(['custodian_id'], ['custodian.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_account_account_number'), 'account', ['account_number'], unique=False)
    op.create_index(op.f('ix_account_billable'), 'account', ['billable'], unique=False)
    op.create_index(op.f('ix_account_discretionary'), 'account', ['discretionary'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_account_discretionary'), table_name='account')
    op.drop_index(op.f('ix_account_billable'), table_name='account')
    op.drop_index(op.f('ix_account_account_number'), table_name='account')
    op.drop_table('account')
    op.drop_index(op.f('ix_client_work_phone'), table_name='client')
    op.drop_index(op.f('ix_client_middle_name'), table_name='client')
    op.drop_index(op.f('ix_client_last_name'), table_name='client')
    op.drop_index(op.f('ix_client_home_phone'), table_name='client')
    op.drop_index(op.f('ix_client_first_name'), table_name='client')
    op.drop_index(op.f('ix_client_email'), table_name='client')
    op.drop_index(op.f('ix_client_dob'), table_name='client')
    op.drop_index(op.f('ix_client_cell_phone'), table_name='client')
    op.drop_table('client')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_group_name'), table_name='group')
    op.drop_table('group')
    op.drop_index(op.f('ix_custodian_name'), table_name='custodian')
    op.drop_table('custodian')
    # ### end Alembic commands ###