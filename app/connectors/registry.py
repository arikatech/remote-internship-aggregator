from __future__ import annotations

from app.connectors.rss import RssConnector
from app.connectors.greenhouse import GreenhouseConnector
from app.connectors.lever import LeverConnector
from app.connectors.html import HtmlConnector


CONNECTORS = {
    "rss": RssConnector(),
    "greenhouse": GreenhouseConnector(),
    "lever": LeverConnector(),
    "html": HtmlConnector(),
}


def get_connector(source_type: str):
    t = (source_type or "").lower().strip()
    if t not in CONNECTORS:
        raise ValueError(f"Unsupported source type: {source_type}")
    return CONNECTORS[t]