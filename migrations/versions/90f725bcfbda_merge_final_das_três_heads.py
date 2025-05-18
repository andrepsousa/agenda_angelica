"""Merge final das três heads

Revision ID: 90f725bcfbda
Revises: 6859e8083c0c, fb668eb8121e, b9e45599beef
Create Date: 2025-05-13 21:11:29.988921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90f725bcfbda'
down_revision = ('6859e8083c0c', 'fb668eb8121e', 'b9e45599beef')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
