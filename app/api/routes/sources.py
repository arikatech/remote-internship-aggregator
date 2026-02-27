from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.usecases.ingest_source import IngestSourceUseCase

from sqlalchemy import select
from app.db.models.source import Source
from app.domain.schemas.source import SourceCreate
from app.connectors.registry import get_connector 

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

@router.post("/sources", status_code=201)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)) -> dict:
    # Validate connector type early (fail fast)
    try:
        get_connector(payload.type)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Unknown source type: {payload.type}")

    existing = (
        db.query(Source)
        .filter(Source.base_url == payload.base_url)
        .one_or_none()
    )
    if existing:
        return {
            "id": existing.id,
            "name": existing.name,
            "type": existing.type,
            "base_url": existing.base_url,
            "is_active": existing.is_active,
            "note": "already existed",
        }

    src = Source(
        name=payload.name,
        type=payload.type,
        base_url=payload.base_url,
        is_active=payload.is_active,
    )
    db.add(src)
    db.commit()
    db.refresh(src)

    return {
        "id": src.id,
        "name": src.name,
        "type": src.type,
        "base_url": src.base_url,
        "is_active": src.is_active,
    }