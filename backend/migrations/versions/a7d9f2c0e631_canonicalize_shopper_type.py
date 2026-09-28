"""Canonicalize shopper category spelling.

Revision ID: a7d9f2c0e631
Revises: 847d4b974cf8
"""

from alembic import op

revision = "a7d9f2c0e631"
down_revision = "847d4b974cf8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE clothing SET type = 'Шопери' WHERE type IN ('Шоппери', 'шоппери')")


def downgrade() -> None:
    # Original spelling cannot be recovered for rows already named Шопери.
    pass
