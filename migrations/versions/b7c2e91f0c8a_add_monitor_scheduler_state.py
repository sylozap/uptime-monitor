"""Add monitor scheduler state

Revision ID: b7c2e91f0c8a
Revises: 4aae7c041f40
Create Date: 2026-05-12 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7c2e91f0c8a"
down_revision: str | Sequence[str] | None = "4aae7c041f40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "monitors",
        sa.Column("last_scheduled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "monitors",
        sa.Column("next_check_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_monitors_is_active_next_check_at"),
        "monitors",
        ["is_active", "next_check_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_monitors_is_active_next_check_at"), table_name="monitors")
    op.drop_column("monitors", "next_check_at")
    op.drop_column("monitors", "last_scheduled_at")
