"""Ajout des champs interim et interimaire

Revision ID: d2b8e04177e0
Revises: be3884cb1890
Create Date: 2025-02-07 10:23:37.388930

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2b8e04177e0'
down_revision = 'be3884cb1890'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('responsable', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interimaire', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('responsable', schema=None) as batch_op:
        batch_op.drop_column('interimaire')

    # ### end Alembic commands ###
