from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from app.connectors.base import FetchContext
from app.connectors.registry import get_connector
from app.db.models.source import Source
from app.db.models.ingestion_run import IngestionRun
from app.domain.usecases.ingest_job import IngestJobUseCase

from app.core.config import settings
from app.infra.telegram.client import TelegramClient
from app.domain.usecases.notify_subscriptions import NotifySubscriptionsUseCase


class IngestSourceUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, source_id: int) -> dict:
        source = self.db.get(Source, source_id)
        if not source or not source.is_active:
            raise ValueError("Source not found or inactive")

        run = IngestionRun(
            source_id=source.id,
            started_at=datetime.utcnow(),
            status="running",
            jobs_found=0,
            jobs_inserted=0,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        connector = get_connector(source.type)
        ctx = FetchContext(
            source_id=source.id,
            source_name=source.name,
            base_url=source.base_url,
        )

        ingest_job = IngestJobUseCase(self.db)

        notifier: NotifySubscriptionsUseCase | None = None
        if settings.telegram_bot_token:
            tg = TelegramClient(settings.telegram_bot_token)
            notifier = NotifySubscriptionsUseCase(self.db, tg)

        inserted = 0
        found = 0

        try:
            for job_create in connector.fetch(ctx):
                found += 1
                job, created = ingest_job.execute(job_create)

                if created:
                    inserted += 1
                    if notifier:
                        notifier.execute_for_new_job(job)

            run.finished_at = datetime.utcnow()
            run.jobs_found = found
            run.jobs_inserted = inserted
            run.status = "success"
            self.db.commit()

            return {"source_id": source.id, "found": found, "inserted": inserted}

        except Exception as e:
            self.db.rollback()  # important: clear failed transaction state

            run.finished_at = datetime.utcnow()
            run.status = "failed"
            run.error = str(e)[:500]
            self.db.add(run)
            self.db.commit()
            raise