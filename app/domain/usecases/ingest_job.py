from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.domain.schemas.job import JobCreate
from app.domain.tagging.engine import compute_tags
from app.utils.fingerprint import generate_fingerprint
from app.utils.url import canonicalize_url


class IngestJobUseCase:
    def __init__(self, db: Session):
        self.db = db

    def _compute_tags(self, data: JobCreate, canonical_url: str) -> list[str]:
        return compute_tags(
            title=data.title,
            company=data.company,
            location=data.location,
            description=data.description,
            url=str(data.url) if data.url else canonical_url,
            remote=getattr(data, "remote", None),
        )

    def _touch_existing(self, existing: Job, data: JobCreate, now: datetime) -> None:
        # Always update last_seen
        existing.last_seen_at = now

        # Backfill tags (and keep deterministic)
        if not existing.tags:
            canonical_url = existing.canonical_url
            existing.tags = self._compute_tags(data, canonical_url)

        # Optional light enrichment (production-friendly, still simple):
        if existing.description is None and data.description:
            existing.description = data.description
            # recompute tags if we enriched the text
            existing.tags = self._compute_tags(data, existing.canonical_url)

        if existing.remote is False and getattr(data, "remote", False) is True:
            existing.remote = True
            if "remote" not in existing.tags:
                existing.tags = sorted(set(existing.tags) | {"remote"})

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
            self._touch_existing(existing, data, now)
            self.db.commit()
            return existing, False

        # 2) external_id
        if data.external_id:
            existing = self.db.execute(
                select(Job).where(Job.external_id == data.external_id)
            ).scalar_one_or_none()
            if existing:
                self._touch_existing(existing, data, now)
                self.db.commit()
                return existing, False

        # 3) fingerprint
        existing = self.db.execute(
            select(Job).where(Job.fingerprint == fingerprint)
        ).scalar_one_or_none()
        if existing:
            self._touch_existing(existing, data, now)
            self.db.commit()
            return existing, False

        # 4) create new
        tags = self._compute_tags(data, canonical_url)

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
            tags=tags,
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job, True