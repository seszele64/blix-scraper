"""URL helper utilities."""

DEFAULT_BASE_URL = "https://blix.pl"


def absolutize_url(url: str, base_url: str | None = None) -> str:
    """Convert a relative URL to an absolute URL.

    Args:
        url: The URL to absolutize. Can be relative or absolute.
        base_url: The base URL to use for relative URLs.
            Defaults to DEFAULT_BASE_URL if not provided.

    Returns:
        The absolute URL.

    Examples:
        >>> absolutize_url("/offers", "https://blix.pl")
        'https://blix.pl/offers'
        >>> absolutize_url("https://example.com")
        'https://example.com'
        >>> absolutize_url("", "https://blix.pl")
        'https://blix.pl'
    """
    base = base_url or DEFAULT_BASE_URL
    if not url:
        return base
    if url.startswith(("http://", "https://")):
        return url
    if url.startswith("/"):
        return f"{base.rstrip('/')}{url}"
    return f"{base}/{url}"
