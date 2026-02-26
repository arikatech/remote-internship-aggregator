from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.job import Job
from app.domain.usecases.list_jobs import ListJobsParams, ListJobsUseCase
from app.domain.schemas.job import JobOut

def _parse_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    items = [v.strip().lower() for v in value.split(",") if v.strip()]
    return items or None

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(Job).order_by(Job.id.desc()).limit(limit).offset(offset)
    ).scalars().all()

    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "remote": j.remote,
            "url": j.url,
            "canonical_url": j.canonical_url,
            "external_id": j.external_id,
            "source_id": j.source_id,
            "published_at": j.published_at,
            "first_seen_at": j.first_seen_at,
            "last_seen_at": j.last_seen_at,
        }
        for j in rows
    ]

@router.get("/jobs")
def list_jobs(
    q: str | None = Query(default=None),
    tags: str | None = Query(default=None),
    tags_mode: str = Query(default="any", pattern="^(any|all)$"),
    source_id: int | None = Query(default=None),
    internship_only: bool = Query(default=False),
    remote: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="recent", pattern="^(recent)$"),
    db: Session = Depends(get_db),
):
    params = ListJobsParams(
        q=q,
        tags=_parse_csv(tags),
        tags_mode="all" if tags_mode == "all" else "any",
        source_id=source_id,
        internship_only=internship_only,
        remote=remote,
        limit=limit,
        offset=offset,
        sort="recent",
    )

    jobs, total = ListJobsUseCase(db).execute(params)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [JobOut.model_validate(j) for j in jobs],
    }


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        return {"detail": "Not found"}
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "remote": job.remote,
        "url": job.url,
        "canonical_url": job.canonical_url,
        "external_id": job.external_id,
        "source_id": job.source_id,
        "description": job.description,
        "published_at": job.published_at,
        "first_seen_at": job.first_seen_at,
        "last_seen_at": job.last_seen_at,
    }