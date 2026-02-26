from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.subscription import Subscription  # adjust to your path


class MatchSubscriptionsUseCase:
    def __init__(self, db: Session) -> None:
        self.db = db

    def execute(self, job: Job) -> list[Subscription]:
        subs = self.db.execute(
            select(Subscription).where(Subscription.is_active == True)  # noqa: E712
        ).scalars().all()

        matched: list[Subscription] = []
        job_text = f"{job.title} {job.company} {job.description or ''}".lower()
        job_tags = set(job.tags or [])

        for s in subs:
            if s.source_id is not None and s.source_id != job.source_id:
                continue

            if s.remote is True and "remote" not in job_tags:
                continue
            if s.remote is False and "remote" in job_tags:
                continue

            if s.internship_only and "internship" not in job_tags:
                continue

            if s.q and s.q.lower() not in job_text:
                continue

            wanted = [t.lower() for t in (s.tags or [])]
            if wanted:
                if s.tags_mode == "all":
                    if not set(wanted).issubset(job_tags):
                        continue
                else:  # any
                    if job_tags.isdisjoint(set(wanted)):
                        continue

            matched.append(s)

        return matched