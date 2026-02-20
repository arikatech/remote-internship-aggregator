from __future__ import annotations
from datetime import datetime
from typing import Iterable

import httpx

from app.connectors.base import FetchContext
from app.domain.schemas.job import JobCreate


class LeverConnector:
    def fetch(self, ctx: FetchContext) -> Iterable[JobCreate]:
        with httpx.Client(timeout=20.0) as client:
            r = client.get(ctx.base_url)
            r.raise_for_status()
            data = r.json()

        for j in data:
            url = j.get("hostedUrl") or j.get("applyUrl")
            if not url:
                continue

            published = None
            ts = j.get("createdAt") or j.get("updatedAt")
            if isinstance(ts, (int, float)):
                published = datetime.fromtimestamp(ts / 1000)

            categories = j.get("categories") or {}
            location = categories.get("location")

            yield JobCreate(
                source_id=ctx.source_id,
                title=j.get("text") or "Untitled",
                company=ctx.source_name,
                location=location,
                remote=False,
                url=url,
                external_id=j.get("id"),
                description=None,
                published_at=published,
            )