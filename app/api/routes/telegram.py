from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.usecases.telegram_bot import TelegramBotUseCase
from app.infra.telegram.client import TelegramClient

log = logging.getLogger("telegram.webhook")

router = APIRouter(prefix="/telegram", tags=["telegram"])


def _process_update(update: dict[str, Any]) -> None:
    """
    Runs after we've already returned 200 OK to Telegram.
    """
    db: Session = SessionLocal()
    try:
        tg = TelegramClient(settings.telegram_bot_token)  # type: ignore[arg-type]
        uc = TelegramBotUseCase(db, tg)
        uc.handle_update(update)
    except Exception as e:
        log.exception("failed processing telegram update", extra={"error": str(e)})
    finally:
        db.close()


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=400, detail="Telegram bot token not configured")

    update: dict[str, Any] = await request.json()

    # Quick debug line (optional but helpful)
    log.info("update received", extra={"update_keys": list(update.keys())})

    # Return immediately; do the heavy work after
    background_tasks.add_task(_process_update, update)

    return {"ok": True}