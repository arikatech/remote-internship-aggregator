from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
}


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)

    # remove tracking query params
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [
        (k, v) for k, v in query_params if k.lower() not in TRACKING_PARAMS
    ]

    new_query = urlencode(filtered)

    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        query=new_query,
        fragment=""
    )

    return urlunparse(normalized)