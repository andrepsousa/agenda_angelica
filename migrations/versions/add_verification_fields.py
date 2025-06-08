"""add verification fields

Revision ID: add_verification_fields
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_verification_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona colunas de verificação à tabela agendamentos
    op.add_column('agendamentos', sa.Column('codigo_verificacao', sa.String(6), nullable=True))
    op.add_column('agendamentos', sa.Column('validade_codigo', sa.DateTime(), nullable=True))
    
    # Atualiza o status padrão para 'pendente'
    op.execute("UPDATE agendamentos SET status = 'pendente' WHERE status IS NULL")


def downgrade():
    # Remove as colunas de verificação
    op.drop_column('agendamentos', 'validade_codigo')
    op.drop_column('agendamentos', 'codigo_verificacao') 