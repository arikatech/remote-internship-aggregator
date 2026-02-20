from __future__ import annotations
from typing import Iterable

import httpx

from app.connectors.base import FetchContext
from app.connectors.parsers.html_parser import extract_job_links
from app.domain.schemas.job import JobCreate


class HtmlConnector:
    def fetch(self, ctx: FetchContext) -> Iterable[JobCreate]:
        with httpx.Client(timeout=20.0) as client:
            r = client.get(ctx.base_url)
            r.raise_for_status()
            html = r.text

        for title, url in extract_job_links(html, ctx.base_url):
            yield JobCreate(
                source_id=ctx.source_id,
                title=title,
                company=ctx.source_name,
                location=None,
                remote=False,
                url=url,
                external_id=None,
                description=None,
                published_at=None,
            )