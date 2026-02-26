from __future__ import annotations

import asyncio
import logging
import time

from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models.source import Source
from app.domain.usecases.ingest_source import IngestSourceUseCase

log = logging.getLogger("scheduler")

_in_process_lock = asyncio.Lock()


def _try_db_lock(session) -> bool:
    if not settings.scheduler_use_db_lock:
        return True
    try:
        got = session.execute(
            text("SELECT pg_try_advisory_lock(:k)"),
            {"k": settings.scheduler_db_lock_key},
        ).scalar()
        return bool(got)
    except Exception:
        return True


def _release_db_lock(session) -> None:
    if not settings.scheduler_use_db_lock:
        return
    try:
        session.execute(
            text("SELECT pg_advisory_unlock(:k)"),
            {"k": settings.scheduler_db_lock_key},
        )
    except Exception:
        pass


def _ingest_one_source(source_id: int) -> dict:
    db = SessionLocal()
    try:
        uc = IngestSourceUseCase(db)
        return uc.execute(source_id)
    finally:
        db.close()


async def ingest_all_job() -> None:
    if _in_process_lock.locked():
        log.info("ingest_all skipped (already running)")
        return

    async with _in_process_lock:
        start = time.time()

        # Session only for lock + listing sources (not shared with threads)
        session = SessionLocal()
        got_lock = False
        ok = 0
        fail = 0

        try:
            got_lock = _try_db_lock(session)
            if not got_lock:
                log.info("ingest_all skipped (db lock not acquired)")
                return

            source_ids = [
                row[0]
                for row in session.query(Source.id)
                .filter(Source.is_active == True)  # noqa: E712
                .all()
            ]

            log.info("ingest_all starting", extra={"sources": len(source_ids)})

            for sid in source_ids:
                try:
                    res = await asyncio.to_thread(_ingest_one_source, sid)
                    ok += 1
                    log.info(
                        "source ingested",
                        extra={
                            "source_id": sid,
                            "found": res.get("found"),
                            "inserted": res.get("inserted"),
                        },
                    )
                except Exception as e:
                    fail += 1
                    log.exception(
                        "source ingestion failed",
                        extra={"source_id": sid, "error": str(e)},
                    )

            elapsed_ms = int((time.time() - start) * 1000)
            log.info(
                "ingest_all done",
                extra={"ok": ok, "fail": fail, "duration_ms": elapsed_ms},
            )

        finally:
            if got_lock:
                _release_db_lock(session)
            session.close()