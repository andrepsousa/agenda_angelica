"""Aumentar tamanho do password_hash para 255 caracteres

Revision ID: fb668eb8121e
Revises: c7c804c0c36d
Create Date: 2025-05-04 18:50:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fb668eb8121e'
down_revision = 'c7c804c0c36d'
branch_labels = None
depends_on = None


def upgrade():
    # Alterar tamanho da coluna password_hash para 255
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.alter_column(
            'password_hash',
            existing_type=sa.String(length=128),
            type_=sa.String(length=255),
            existing_nullable=True
        )


def downgrade():
    # Reverter tamanho da coluna password_hash para 128
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.alter_column(
            'password_hash',
            existing_type=sa.String(length=255),
            type_=sa.String(length=128),
            existing_nullable=True
        )
