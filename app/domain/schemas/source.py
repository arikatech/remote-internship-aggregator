from __future__ import annotations

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    type: str = Field(..., min_length=2, max_length=30)
    base_url: str = Field(..., min_length=5, max_length=500)
    is_active: bool = True