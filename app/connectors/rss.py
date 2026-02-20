from __future__ import annotations
from datetime import datetime
from typing import Iterable

import feedparser

from app.connectors.base import FetchContext
from app.domain.schemas.job import JobCreate


def _parse_dt(entry) -> datetime | None:
    # feedparser may provide published_parsed / updated_parsed
    for key in ("published_parsed", "updated_parsed"):
        st = entry.get(key)
        if st:
            return datetime(*st[:6])
    return None


class RssConnector:
    def fetch(self, ctx: FetchContext) -> Iterable[JobCreate]:
        feed = feedparser.parse(ctx.base_url)

        for e in feed.entries:
            url = e.get("link")
            if not url:
                continue

            title = e.get("title") or "Untitled"
            description = e.get("summary")

            yield JobCreate(
                source_id=ctx.source_id,
                title=title,
                company=ctx.source_name,   # RSS often doesn't provide company cleanly
                location=None,
                remote=False,
                url=url,
                external_id=None,
                description=description,
                published_at=_parse_dt(e),
            )