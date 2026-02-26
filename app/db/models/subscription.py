from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Destination
    telegram_chat_id: Mapped[str] = mapped_column(String(64), nullable=False)

    # Filters (simple but powerful)
    q: Mapped[str | None] = mapped_column(String(300), nullable=True)

    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}",
    )
    tags_mode: Mapped[str] = mapped_column(String(10), nullable=False, default="any")

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id"), nullable=True
    )
    remote: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    internship_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_subscriptions_is_active", "is_active"),
        Index("ix_subscriptions_tags_gin", "tags", postgresql_using="gin"),
    )