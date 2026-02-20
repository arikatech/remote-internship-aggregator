from __future__ import annotations

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.domain.schemas.job import JobCreate
from app.utils.fingerprint import generate_fingerprint
from app.utils.url import canonicalize_url


class IngestJobUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, data: JobCreate) -> tuple[Job, bool]:
        """
        Returns: (job, created)
        created=True if a new DB row was inserted, else False.
        """
        canonical_url = canonicalize_url(str(data.url))
        fingerprint = generate_fingerprint(
            title=data.title,
            company=data.company,
            location=data.location,
            canonical_url=canonical_url,
        )

        now = datetime.utcnow()

        # 1) canonical_url
        existing = self.db.execute(
            select(Job).where(Job.canonical_url == canonical_url)
        ).scalar_one_or_none()
        if existing:
            existing.last_seen_at = now
            self.db.commit()
            return existing, False

        # 2) external_id
        if data.external_id:
            existing = self.db.execute(
                select(Job).where(Job.external_id == data.external_id)
            ).scalar_one_or_none()
            if existing:
                existing.last_seen_at = now
                self.db.commit()
                return existing, False

        # 3) fingerprint
        existing = self.db.execute(
            select(Job).where(Job.fingerprint == fingerprint)
        ).scalar_one_or_none()
        if existing:
            existing.last_seen_at = now
            self.db.commit()
            return existing, False

        # 4) create new
        job = Job(
            title=data.title,
            company=data.company,
            location=data.location,
            remote=data.remote,
            url=str(data.url),
            canonical_url=canonical_url,
            external_id=data.external_id,
            fingerprint=fingerprint,
            description=data.description,
            source_id=data.source_id,
            published_at=data.published_at,
            created_at=now,
            first_seen_at=now,
            last_seen_at=now,
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job, True