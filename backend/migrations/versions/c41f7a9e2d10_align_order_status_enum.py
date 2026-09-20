"""align order status enum with the model

Revision ID: c41f7a9e2d10
Revises: b8c702ba686d
Create Date: 2026-09-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c41f7a9e2d10'
down_revision: Union[str, Sequence[str], None] = 'b8c702ba686d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enum orderstatus: PENDING/PAID/SHIPPED/CANCELLED -> created/processing/paid/failure."""
    op.execute('ALTER TABLE "order" ALTER COLUMN status DROP DEFAULT')
    op.execute('ALTER TABLE "order" ALTER COLUMN status TYPE text USING status::text')
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("CREATE TYPE orderstatus AS ENUM ('created', 'processing', 'paid', 'failure')")
    op.execute(
        """
        UPDATE "order" SET status = CASE status
            WHEN 'PENDING' THEN 'created'
            WHEN 'PAID' THEN 'paid'
            WHEN 'SHIPPED' THEN 'paid'
            WHEN 'CANCELLED' THEN 'failure'
            ELSE status
        END
        """
    )
    op.execute('ALTER TABLE "order" ALTER COLUMN status TYPE orderstatus USING status::orderstatus')
    op.execute("""ALTER TABLE "order" ALTER COLUMN status SET DEFAULT 'created'""")


def downgrade() -> None:
    """Back to PENDING/PAID/SHIPPED/CANCELLED."""
    op.execute('ALTER TABLE "order" ALTER COLUMN status DROP DEFAULT')
    op.execute('ALTER TABLE "order" ALTER COLUMN status TYPE text USING status::text')
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("CREATE TYPE orderstatus AS ENUM ('PENDING', 'PAID', 'SHIPPED', 'CANCELLED')")
    op.execute(
        """
        UPDATE "order" SET status = CASE status
            WHEN 'created' THEN 'PENDING'
            WHEN 'processing' THEN 'PENDING'
            WHEN 'paid' THEN 'PAID'
            WHEN 'failure' THEN 'CANCELLED'
            ELSE status
        END
        """
    )
    op.execute('ALTER TABLE "order" ALTER COLUMN status TYPE orderstatus USING status::orderstatus')
    op.execute("""ALTER TABLE "order" ALTER COLUMN status SET DEFAULT 'PENDING'""")
