import hashlib


def generate_fingerprint(
    title: str,
    company: str,
    location: str | None,
    canonical_url: str,
) -> str:
    base = f"{title}|{company}|{location or ''}|{canonical_url}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()