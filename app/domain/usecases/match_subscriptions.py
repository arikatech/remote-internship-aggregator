from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.subscription import Subscription


class MatchSubscriptionsUseCase:
    def __init__(self, db: Session) -> None:
        self.db = db

    def execute(self, job: Job) -> list[Subscription]:
        subs = (
            self.db.execute(select(Subscription).where(Subscription.is_active == True))  # noqa: E712
            .scalars()
            .all()
        )

        matched: list[Subscription] = []
        job_text = f"{job.title} {job.company} {job.description or ''}".lower()
        job_tags = set(job.tags or [])

        for s in subs:
            # source filter
            if s.source_id is not None and s.source_id != job.source_id:
                continue

            # remote filter (use boolean column)
            if s.remote is True and not job.remote:
                continue
            if s.remote is False and job.remote:
                continue

            # internship-only filter (trust tagging engine)
            if s.internship_only and "internship" not in job_tags:
                continue

            # optional keyword query filter
            if s.q and s.q.strip():
                if s.q.lower() not in job_text:
                    continue

            # tags filter
            wanted = [t.strip().lower() for t in (s.tags or []) if (t or "").strip()]
            if wanted:
                wanted_set = set(wanted)
                mode = (s.tags_mode or "any").lower()
                if mode == "all":
                    if not wanted_set.issubset(job_tags):
                        continue
                else:  # any
                    if job_tags.isdisjoint(wanted_set):
                        continue

            matched.append(s)

        return matched