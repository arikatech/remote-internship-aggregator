from pydantic import BaseModel, HttpUrl
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