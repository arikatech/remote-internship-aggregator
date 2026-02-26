"""add job tags

Revision ID: 02b165122746
Revises: 1e085fb299e3
Create Date: 2026-02-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "02b165122746"
down_revision: Union[str, Sequence[str], None] = "1e085fb299e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "jobs",
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
    )
    op.create_index(
        "ix_jobs_tags_gin",
        "jobs",
        ["tags"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_jobs_tags_gin", table_name="jobs")
    op.drop_column("jobs", "tags")