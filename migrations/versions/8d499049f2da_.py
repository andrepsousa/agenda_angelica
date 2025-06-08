"""empty message

Revision ID: 8d499049f2da
Revises: 2bf58c2eba72, fix_user_foreign_key
Create Date: 2025-06-08 12:30:14.835791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d499049f2da'
down_revision = ('2bf58c2eba72', 'fix_user_foreign_key')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
