from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes.health import router as health_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.sources import router as sources_router
from app.api.routes.jobs import router as jobs_router

def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(ingestion_router)
    app.include_router(sources_router)
    app.include_router(jobs_router)

    @app.get("/")
    async def root():
        return {"app": settings.app_name, "env": settings.env}

    return app


app = create_app()
