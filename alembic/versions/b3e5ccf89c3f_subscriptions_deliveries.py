"""subscriptions + deliveries

Revision ID: b3e5ccf89c3f
Revises: 02b165122746
Create Date: 2026-02-24 15:07:51.675658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b3e5ccf89c3f"
down_revision: Union[str, Sequence[str], None] = "02b165122746"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Relax legacy email/keyword so we can move away from them
    op.alter_column(
        "subscriptions",
        "email",
        existing_type=sa.String(length=320),
        nullable=True,
    )
    op.alter_column(
        "subscriptions",
        "keyword",
        existing_type=sa.String(length=200),
        nullable=True,
    )

    # Add new subscription fields (Telegram + matching rules)
    op.add_column(
        "subscriptions",
        sa.Column("telegram_chat_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column("q", sa.String(length=300), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "subscriptions",
        sa.Column("tags_mode", sa.String(length=10), nullable=False, server_default="any"),
    )
    op.add_column(
        "subscriptions",
        sa.Column("source_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column("remote", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column("internship_only", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    # Index for fast tag matching
    op.create_index(
        "ix_subscriptions_tags_gin",
        "subscriptions",
        ["tags"],
        unique=False,
        postgresql_using="gin",
    )

    # Create notification deliveries table (notify-once enforced by unique constraint)
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "subscription_id",
            sa.Integer(),
            sa.ForeignKey("subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            sa.Integer(),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("subscription_id", "job_id", name="uq_delivery_sub_job"),
    )


def downgrade() -> None:
    op.drop_table("notification_deliveries")

    op.drop_index("ix_subscriptions_tags_gin", table_name="subscriptions")

    op.drop_column("subscriptions", "internship_only")
    op.drop_column("subscriptions", "remote")
    op.drop_column("subscriptions", "source_id")
    op.drop_column("subscriptions", "tags_mode")
    op.drop_column("subscriptions", "tags")
    op.drop_column("subscriptions", "q")
    op.drop_column("subscriptions", "telegram_chat_id")

    op.alter_column(
        "subscriptions",
        "keyword",
        existing_type=sa.String(length=200),
        nullable=False,
    )
    op.alter_column(
        "subscriptions",
        "email",
        existing_type=sa.String(length=320),
        nullable=False,
    )