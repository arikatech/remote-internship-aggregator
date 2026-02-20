from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.usecases.ingest_source import IngestSourceUseCase

from sqlalchemy import select
from app.db.models.source import Source

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/{source_id}/ingest")
def ingest_source(source_id: int, db: Session = Depends(get_db)):
    try:
        return IngestSourceUseCase(db).execute(source_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("")
def list_sources(db: Session = Depends(get_db)):
    sources = db.execute(select(Source).order_by(Source.id.asc())).scalars().all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "type": s.type,
            "base_url": s.base_url,
            "is_active": s.is_active,
            "created_at": s.created_at,
        }
        for s in sources
    ]

@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    src = db.get(Source, source_id)
    if not src:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(src)
    db.commit()
    return {"deleted": source_id}


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