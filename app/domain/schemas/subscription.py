from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    telegram_chat_id: str

    q: str | None = None
    tags: list[str] = Field(default_factory=list)
    tags_mode: str = "any"  # "any" or "all"
    source_id: int | None = None
    remote: bool | None = None
    internship_only: bool = False


class SubscriptionOut(BaseModel):
    id: int
    telegram_chat_id: str
    q: str | None = None
    tags: list[str] = Field(default_factory=list)
    tags_mode: str
    source_id: int | None = None
    remote: bool | None = None
    internship_only: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}