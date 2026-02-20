from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Iterable

from app.domain.schemas.job import JobCreate


@dataclass(frozen=True)
class FetchContext:
    source_id: int
    source_name: str
    base_url: str


class Connector(Protocol):
    def fetch(self, ctx: FetchContext) -> Iterable[JobCreate]:
        ...