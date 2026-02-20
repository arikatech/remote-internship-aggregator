from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    jobs_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    status: Mapped[str] = mapped_column(String(30), default="success", nullable=False)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
