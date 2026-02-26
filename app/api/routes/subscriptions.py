from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.subscription import Subscription
from app.domain.schemas.subscription import SubscriptionCreate, SubscriptionOut


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionOut)
def create_subscription(data: SubscriptionCreate, db: Session = Depends(get_db)):
    sub = Subscription(
        telegram_chat_id=data.telegram_chat_id,
        q=data.q,
        tags=data.tags,
        tags_mode=data.tags_mode,
        source_id=data.source_id,
        remote=data.remote,
        internship_only=data.internship_only,
        is_active=True,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return SubscriptionOut.model_validate(sub)


@router.get("", response_model=list[SubscriptionOut])
def list_subscriptions(db: Session = Depends(get_db)):
    subs = db.execute(select(Subscription).order_by(Subscription.id.desc())).scalars().all()
    return [SubscriptionOut.model_validate(s) for s in subs]