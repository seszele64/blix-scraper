"""Price parsing utilities using the price-parser library."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

import price_parser


def parse_price(raw: object) -> Optional[Decimal]:
    """Parse a price string into a Decimal with 2 decimal places.

    Uses the price-parser library to handle various price formats,
    including Polish formats with commas and złoty symbols.

    Args:
        raw: Raw price value (string, Decimal, int, float, or None).

    Returns:
        Decimal rounded to 2 decimal places, or None if parsing fails
        or input is empty/None.
    """
    if raw is None:
        return None

    raw_str = str(raw).strip()
    if not raw_str:
        return None

    parsed = price_parser.Price.fromstring(raw_str)

    if parsed.amount is None:
        return None

    return Decimal(str(parsed.amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
