from __future__ import annotations

import re

from app.domain.tagging.rules import REMOTE_KEYWORDS, TAG_RULES


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _contains_word(text: str, word: str) -> bool:
    pattern = rf"\b{re.escape(word)}\b"
    return re.search(pattern, text) is not None


def compute_tags(
    *,
    title: str | None,
    company: str | None,
    location: str | None,
    description: str | None,
    url: str | None,
    remote: bool | None,
) -> list[str]:
    parts = [title, company, location, description, url]
    text = _normalize(" ".join([p for p in parts if p]))

    tags: set[str] = set()

    # remote tag: structured field wins, else keyword detection
    if remote is True:
        tags.add("remote")
    else:
        for kw in REMOTE_KEYWORDS:
            if kw in text:
                tags.add("remote")
                break

    for tag, keywords in TAG_RULES.items():
        for kw in keywords:
            kw_norm = _normalize(kw)
            # short terms like "go", "ts" => word boundary
            if len(kw_norm) <= 3:
                if _contains_word(text, kw_norm.strip()):
                    tags.add(tag)
                    break
            else:
                if kw_norm in text:
                    tags.add(tag)
                    break

    return sorted(tags)