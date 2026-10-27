"""Add user.is_banned.

Revision ID: e2b4c6d8f013
Revises: a7d9f2c0e631
"""

import sqlalchemy as sa
from alembic import op

revision = "e2b4c6d8f013"
down_revision = "a7d9f2c0e631"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("is_banned", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("user", "is_banned")
