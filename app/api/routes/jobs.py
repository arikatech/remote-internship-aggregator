from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.job import Job

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