from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes.health import router as health_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.sources import router as sources_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.subscriptions import router as subscriptions_router
from app.scheduler.scheduler import start_scheduler, shutdown_scheduler
from app.api.routes.telegram import router as telegram_router
from app.core.migrations import run_migrations_if_enabled

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()


def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    run_migrations_if_enabled()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(health_router)
    app.include_router(ingestion_router)
    app.include_router(sources_router)
    app.include_router(jobs_router)
    app.include_router(subscriptions_router)
    app.include_router(telegram_router)

    @app.get("/")
    async def root():
        return {"app": settings.app_name, "env": settings.env}

    return app


app = create_app()