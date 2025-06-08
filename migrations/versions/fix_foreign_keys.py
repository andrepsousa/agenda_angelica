"""fix foreign keys

Revision ID: fix_foreign_keys
Revises: add_verification_fields
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_foreign_keys'
down_revision = 'add_verification_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Remove a chave estrangeira antiga
    op.drop_constraint('agendamentos_cliente_id_fkey', 'agendamentos', type_='foreignkey')
    
    # Adiciona a nova chave estrangeira apontando para a tabela correta
    op.create_foreign_key(
        'agendamentos_cliente_id_fkey',
        'agendamentos', 'usuarios',
        ['cliente_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Remove a nova chave estrangeira
    op.drop_constraint('agendamentos_cliente_id_fkey', 'agendamentos', type_='foreignkey')
    
    # Restaura a chave estrangeira antiga
    op.create_foreign_key(
        'agendamentos_cliente_id_fkey',
        'agendamentos', 'usuarios',
        ['cliente_id'], ['id'],
        ondelete='CASCADE'
    ) 