from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.schemas.job import JobCreate
from app.domain.usecases.ingest_job import IngestJobUseCase

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