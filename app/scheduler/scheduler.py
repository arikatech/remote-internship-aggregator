from __future__ import annotations

import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.scheduler.jobs import ingest_all_job

log = logging.getLogger("scheduler")

_scheduler: Optional[AsyncIOScheduler] = None


def _cron_trigger_from_expr(expr: str) -> CronTrigger:
    """
    Expect 5-part cron: "minute hour day month day_of_week"
    Example: "0 9 * * *"  -> every day at 09:00
    """
    parts = expr.split()
    if len(parts) != 5:
        raise ValueError(
            "SCHEDULER_INGEST_CRON must have 5 fields: 'm h dom mon dow'"
        )
    minute, hour, day, month, day_of_week = parts
    return CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
        timezone=settings.scheduler_timezone,
    )


def start_scheduler() -> None:
    global _scheduler

    if not settings.scheduler_enabled:
        log.info("scheduler disabled")
        return

    if _scheduler is not None:
        return

    sch = AsyncIOScheduler(timezone=settings.scheduler_timezone)

    sch.add_job(
        ingest_all_job,
        trigger=_cron_trigger_from_expr(settings.scheduler_ingest_cron),
        id="ingest_all",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        jitter=settings.scheduler_ingest_jitter_seconds,
    )

    sch.start()
    _scheduler = sch

    log.info(
        "scheduler started",
        extra={
            "tz": settings.scheduler_timezone,
            "cron": settings.scheduler_ingest_cron,
        },
    )


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    _scheduler.shutdown(wait=False)
    _scheduler = None
    log.info("scheduler stopped")