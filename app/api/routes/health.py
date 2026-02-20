from fastapi import APIRouter
from sqlalchemy import text
from app.core.db import get_engine

router = APIRouter()


@router.get("/healthz")
async def health_check():
    engine = get_engine()

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {"status": "ok", "db": "ok"}

    except Exception:
        return {"status": "degraded", "db": "down"}
