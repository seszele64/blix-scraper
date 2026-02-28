"""BeautifulSoup helper utilities."""

from bs4 import BeautifulSoup, Tag


def get_single_attribute(tag: Tag | None, attr: str) -> str | None:
    """Get a single attribute value from a BeautifulSoup tag.

    Args:
        tag: The BeautifulSoup Tag to get the attribute from.
        attr: The attribute name to retrieve.

    Returns:
        The attribute value as a string, or None if not found or empty.

    Examples:
        >>> from bs4 import BeautifulSoup
        >>> soup = BeautifulSoup('<a href="/path">Link</a>', 'html.parser')
        >>> get_single_attribute(soup.a, 'href')
        '/path'
        >>> get_single_attribute(soup.a, 'class')
        None
        >>> get_single_attribute(None, 'href')
        None
    """
    if tag is None:
        return None
    value = tag.get(attr)
    if value is None:
        return None
    if isinstance(value, list):
        return value[0] if value else None
    return value


def get_first_element(soup: BeautifulSoup, selector: str) -> Tag | None:
    """Get the first element matching a CSS selector from a BeautifulSoup object.

    Args:
        soup: The BeautifulSoup object to search in.
        selector: The CSS selector to match elements.

    Returns:
        The first matching Tag, or None if no match is found.

    Examples:
        >>> from bs4 import BeautifulSoup
        >>> soup = BeautifulSoup('<div><span>First</span><span>Second</span></div>', 'html.parser')
        >>> get_first_element(soup, 'span')
        <span>First</span>
        >>> get_first_element(soup, 'nonexistent')
        None
    """
    return soup.select_one(selector)
