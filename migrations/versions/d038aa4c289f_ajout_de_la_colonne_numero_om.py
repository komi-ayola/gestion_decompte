"""Ajout de la colonne numero_om

Revision ID: d038aa4c289f
Revises: c4a93526c3f9
Create Date: 2025-02-04 16:49:52.474450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd038aa4c289f'
down_revision = 'c4a93526c3f9'
branch_labels = None
depends_on = None


def upgrade():
    #  Ajouter la colonne `numero_om` en autorisant temporairement les NULL
    with op.batch_alter_table('decompte', schema=None) as batch_op:
        batch_op.add_column(sa.Column('numero_om', sa.String(length=50), nullable=True))  # ✅ Autoriser NULL d'abord

    #  Mettre une valeur par défaut aux anciennes lignes (ex: 'INCONNU')
    op.execute("UPDATE decompte SET numero_om = 'INCONNU' WHERE numero_om IS NULL")

    #  Appliquer la contrainte NOT NULL après
    with op.batch_alter_table('decompte', schema=None) as batch_op:
        batch_op.alter_column('numero_om', nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('decompte', schema=None) as batch_op:
        batch_op.drop_column('numero_om')

    # ### end Alembic commands ###
