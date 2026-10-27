"""Make user.email NOT NULL and unique.

Revision ID: f3c5d7e9a124
Revises: e2b4c6d8f013

Fails if the table still has NULL or duplicate emails: clean them up first.
"""

import sqlalchemy as sa
from alembic import op

revision = "f3c5d7e9a124"
down_revision = "e2b4c6d8f013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("user", "email", existing_type=sa.Text(), nullable=False)
    op.create_unique_constraint(op.f("uq_user_email"), "user", ["email"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_user_email"), "user", type_="unique")
    op.alter_column("user", "email", existing_type=sa.Text(), nullable=True)
