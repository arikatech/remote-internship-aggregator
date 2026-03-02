from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.source import Source
from app.db.session import get_db
from app.domain.usecases.ingest_source import IngestSourceUseCase

router = APIRouter(prefix="/ops", tags=["ops"])


@router.post("/ingest-all")
def ops_ingest_all(key: str, db: Session = Depends(get_db)) -> dict:
    if not settings.ops_ingest_key:
        raise HTTPException(status_code=500, detail="OPS_INGEST_KEY not configured")

    if key != settings.ops_ingest_key:
        raise HTTPException(status_code=403, detail="forbidden")

    sources = (
        db.query(Source)
        .filter(Source.is_active == True)  # noqa: E712
        .order_by(Source.id.asc())
        .all()
    )

    uc = IngestSourceUseCase(db)

    results: list[dict] = []
    ok = 0
    failed = 0
    total_found = 0
    total_inserted = 0

    for s in sources:
        try:
            res = uc.execute(s.id)
            ok += 1
            total_found += int(res.get("found", 0))
            total_inserted += int(res.get("inserted", 0))
            results.append(
                {
                    "source_id": s.id,
                    "name": s.name,
                    "status": "success",
                    "found": res.get("found", 0),
                    "inserted": res.get("inserted", 0),
                }
            )
        except Exception as e:
            failed += 1
            results.append(
                {
                    "source_id": s.id,
                    "name": s.name,
                    "status": "failed",
                    "error": str(e)[:500],
                }
            )

    return {
        "sources_total": len(sources),
        "sources_success": ok,
        "sources_failed": failed,
        "total_found": total_found,
        "total_inserted": total_inserted,
        "results": results,
    }