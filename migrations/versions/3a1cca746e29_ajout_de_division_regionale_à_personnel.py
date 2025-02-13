"""Ajout de division_regionale à Personnel

Revision ID: 3a1cca746e29
Revises: b512ee1fab2b
Create Date: 2025-02-05 17:07:30.693768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a1cca746e29'
down_revision = 'b512ee1fab2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('personnel', schema=None) as batch_op:
        batch_op.add_column(sa.Column('division_regionale', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('personnel', schema=None) as batch_op:
        batch_op.drop_column('division_regionale')

    # ### end Alembic commands ###
