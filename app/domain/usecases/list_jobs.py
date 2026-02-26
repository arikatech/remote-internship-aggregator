from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.db.models.job import Job


@dataclass(frozen=True)
class ListJobsParams:
    q: str | None = None
    tags: list[str] | None = None
    tags_mode: Literal["any", "all"] = "any"
    source_id: int | None = None
    internship_only: bool = False
    remote: bool | None = None
    limit: int = 50
    offset: int = 0
    sort: Literal["recent"] = "recent"


class ListJobsUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, params: ListJobsParams) -> tuple[list[Job], int]:
        stmt = sa.select(Job)
        count_stmt = sa.select(sa.func.count()).select_from(Job)

        filters: list[sa.ColumnElement[bool]] = []

        if params.source_id is not None:
            filters.append(Job.source_id == params.source_id)

        if params.internship_only:
            filters.append(Job.tags.contains(["internship"]))

        if params.remote is True:
            filters.append(Job.tags.contains(["remote"]))
        elif params.remote is False:
            filters.append(~Job.tags.contains(["remote"]))

        if params.tags:
            wanted = [t.strip().lower() for t in params.tags if t.strip()]
            if wanted:
                if params.tags_mode == "all":
                    filters.append(Job.tags.contains(wanted))
                else:
                    filters.append(Job.tags.overlap(wanted))

        if params.q:
            pattern = f"%{params.q.lower()}%"
            filters.append(
                sa.or_(
                    sa.func.lower(Job.title).like(pattern),
                    sa.func.lower(Job.company).like(pattern),
                    sa.func.lower(Job.description).like(pattern),
                )
            )

        if filters:
            cond = sa.and_(*filters)
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        if params.sort == "recent":
            stmt = stmt.order_by(
                sa.desc(sa.func.coalesce(Job.published_at, Job.last_seen_at, Job.created_at))
            )

        stmt = stmt.limit(params.limit).offset(params.offset)

        jobs = list(self.db.execute(stmt).scalars().all())
        total = int(self.db.execute(count_stmt).scalar_one())
        return jobs, total