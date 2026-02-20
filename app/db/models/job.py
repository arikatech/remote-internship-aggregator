from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    url: Mapped[str] = mapped_column(String(800), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source = relationship("Source")

    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    canonical_url: Mapped[str] = mapped_column(String(800), unique=True, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_jobs_external_id", "external_id"),
        Index("ix_jobs_fingerprint", "fingerprint"),
    )
