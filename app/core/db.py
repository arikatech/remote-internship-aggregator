from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.core.config import settings

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            pool_pre_ping=True,
        )
    return _engine
