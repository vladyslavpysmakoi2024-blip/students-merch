"""add survey responses and completed_survey on user

Revision ID: c3e91a7b4d12
Revises: b8c702ba686d
Create Date: 2026-09-18 10:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "c3e91a7b4d12"
down_revision: Union[str, Sequence[str], None] = "c41f7a9e2d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("completed_survey", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_table(
        "survey_response",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_user", sa.Integer(), nullable=False),
        sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["id_user"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id_user", name="uq_survey_response_user"),
    )
    op.create_index(op.f("ix_survey_response_id"), "survey_response", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_survey_response_id"), table_name="survey_response")
    op.drop_table("survey_response")
    op.drop_column("user", "completed_survey")
