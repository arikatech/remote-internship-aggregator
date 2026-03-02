from __future__ import annotations

from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.notification_delivery import NotificationDelivery
from app.domain.usecases.match_subscriptions import MatchSubscriptionsUseCase
from app.infra.telegram.client import TelegramClient


def format_job_message(job: Job) -> str:
    tags = ", ".join(job.tags or [])
    loc = job.location or "N/A"
    remote = "🌍 Remote" if job.remote else "🏢 On-site/Hybrid"
    return (
        f"🆕 {job.title}\n"
        f"🏢 {job.company}\n"
        f"📍 {loc} • {remote}\n"
        f"🏷 {tags}\n"
        f"🔗 {job.url}"
    )


def build_job_keyboard(job: Job) -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Open 🔗", "url": job.url}],
            [
                {"text": "Pause notifications ⛔", "callback_data": "toggle:active"},
                {"text": "Settings ⚙️", "callback_data": "menu:settings"},
            ],
        ]
    }


class NotifySubscriptionsUseCase:
    def __init__(self, db: Session, telegram: TelegramClient) -> None:
        self.db = db
        self.telegram = telegram

    def execute_for_new_job(self, job: Job) -> int:
        subs = MatchSubscriptionsUseCase(self.db).execute(job)
        sent_count = 0

        for s in subs:
            delivery = NotificationDelivery(
                subscription_id=s.id,
                job_id=job.id,
                status="pending",
                error=None,
                created_at=datetime.utcnow(),
                sent_at=None,
            )
            self.db.add(delivery)

            # Commit first so UNIQUE constraint enforces "notify once"
            try:
                self.db.commit()
            except IntegrityError:
                self.db.rollback()
                continue  # already notified

            try:
                self.telegram.send_message(
                    s.telegram_chat_id,
                    format_job_message(job),
                    reply_markup=build_job_keyboard(job),
                )
                delivery.status = "sent"
                delivery.sent_at = datetime.utcnow()
                sent_count += 1
            except Exception as e:
                delivery.status = "failed"
                delivery.error = str(e)[:2000]

            self.db.commit()

        return sent_count