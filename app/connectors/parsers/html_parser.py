from __future__ import annotations
from bs4 import BeautifulSoup


def extract_job_links(html: str, base_url: str) -> list[tuple[str, str]]:
    """
    Returns list of (title, url).
    Very generic heuristic: collects <a> with href and non-empty text.
    """
    soup = BeautifulSoup(html, "lxml")
    out: list[tuple[str, str]] = []

    for a in soup.select("a[href]"):
        text = (a.get_text() or "").strip()
        href = (a.get("href") or "").strip()
        if not text or not href:
            continue

        # skip anchors/mailto
        if href.startswith("#") or href.startswith("mailto:"):
            continue

        # naive filter: must contain job-ish keywords OR absolute URL
        lowered = (text + " " + href).lower()
        if "job" not in lowered and "career" not in lowered and not href.startswith("http"):
            continue

        # resolve relative URLs simply
        if href.startswith("/"):
            href = base_url.rstrip("/") + href

        out.append((text[:300], href[:800]))

    # de-dup
    seen = set()
    deduped = []
    for t, u in out:
        if u in seen:
            continue
        seen.add(u)
        deduped.append((t, u))

    return deduped