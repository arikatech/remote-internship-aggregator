from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.schemas.job import JobCreate
from app.domain.usecases.ingest_job import IngestJobUseCase
from app.domain.usecases.ingest_source import IngestSourceUseCase


from sqlalchemy import select
from app.db.models.source import Source

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/test")
def test_ingest(
    data: JobCreate,
    db: Session = Depends(get_db),
):
    usecase = IngestJobUseCase(db)
    job = usecase.execute(data)

    return {
        "id": job.id,
        "title": job.title,
        "canonical_url": job.canonical_url,
    }


@router.post("/ingest-all")
def ingest_all_sources(db: Session = Depends(get_db)):
    sources = db.execute(
        select(Source).where(Source.is_active == True).order_by(Source.id.asc())
    ).scalars().all()

    usecase = IngestSourceUseCase(db)

    results = []
    total_found = 0
    total_inserted = 0
    ok = 0
    failed = 0

    for s in sources:
        try:
            r = usecase.execute(s.id)
            results.append({"source_id": s.id, "name": s.name, **r, "status": "success"})
            total_found += r.get("found", 0)
            total_inserted += r.get("inserted", 0)
            ok += 1
        except Exception as e:
            results.append(
                {"source_id": s.id, "name": s.name, "status": "failed", "error": str(e)[:300]}
            )
            failed += 1

    return {
        "sources_total": len(sources),
        "sources_success": ok,
        "sources_failed": failed,
        "total_found": total_found,
        "total_inserted": total_inserted,
        "results": results,
    }