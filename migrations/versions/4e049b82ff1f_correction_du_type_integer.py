"""Correction du type Integer

Revision ID: 4e049b82ff1f
Revises: d2b8e04177e0
Create Date: 2025-02-12 08:50:13.145158

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e049b82ff1f'
down_revision = 'd2b8e04177e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('responsable', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interimaire_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'responsable', ['interimaire_id'], ['id'])
        batch_op.drop_column('interimaire')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('responsable', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interimaire', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('interimaire_id')

    # ### end Alembic commands ###
