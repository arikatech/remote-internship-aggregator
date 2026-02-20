from __future__ import annotations
from datetime import datetime
from typing import Iterable

import httpx

from app.connectors.base import FetchContext
from app.domain.schemas.job import JobCreate


class GreenhouseConnector:
    def fetch(self, ctx: FetchContext) -> Iterable[JobCreate]:
        # ctx.base_url should be the FULL API URL to jobs JSON
        with httpx.Client(timeout=20.0) as client:
            r = client.get(ctx.base_url)
            r.raise_for_status()
            data = r.json()

        for j in data.get("jobs", []):
            url = j.get("absolute_url")
            if not url:
                continue

            published = None
            # Greenhouse often has "updated_at"/"created_at" ISO strings
            for key in ("updated_at", "created_at"):
                s = j.get(key)
                if s:
                    try:
                        published = datetime.fromisoformat(s.replace("Z", "+00:00"))
                    except Exception:
                        published = None
                    break

            yield JobCreate(
                source_id=ctx.source_id,
                title=j.get("title") or "Untitled",
                company=ctx.source_name,
                location=(j.get("location") or {}).get("name"),
                remote=False,
                url=url,
                external_id=str(j.get("id")) if j.get("id") is not None else None,
                description=None,
                published_at=published,
            )