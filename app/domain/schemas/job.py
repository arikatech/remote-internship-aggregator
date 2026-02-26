from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class JobCreate(BaseModel):
    title: str
    company: str
    location: str | None = None
    remote: bool = False

    url: HttpUrl
    external_id: str | None = None
    source_id: int

    description: str | None = None
    published_at: datetime | None = None

class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    remote: bool
    url: str
    canonical_url: str
    external_id: str | None = None
    source_id: int
    description: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    first_seen_at: datetime
    last_seen_at: datetime
    tags: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}