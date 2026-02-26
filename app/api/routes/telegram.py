from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.usecases.telegram_bot import TelegramBotUseCase
from app.infra.telegram.client import TelegramClient

log = logging.getLogger("telegram")

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(request: Request) -> dict:
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=400, detail="Telegram bot token not configured")

    update: dict[str, Any] = await request.json()

    db: Session = SessionLocal()
    try:
        tg = TelegramClient(settings.telegram_bot_token)
        uc = TelegramBotUseCase(db, tg)
        try:
            uc.handle_update(update)
        except Exception as e:
            # Never fail webhook delivery due to business logic issues
            log.exception("failed to handle telegram update", extra={"error": str(e)})
    finally:
        db.close()

    return {"ok": True}