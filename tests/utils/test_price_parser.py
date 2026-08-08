"""Tests for price_parser utility."""

from decimal import Decimal

import pytest

from src.utils.price_parser import parse_price


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # None and empty
        (None, None),
        ("", None),
        ("   ", None),
        # Polish price formats
        ("4,99 zł", Decimal("4.99")),
        ("4.99", Decimal("4.99")),
        ("12,50 zł", Decimal("12.50")),
        ("1 299,00 zł", Decimal("1299.00")),
        # Other currency formats
        ("PLN 10", Decimal("10.00")),
        ("zł 5.50", Decimal("5.50")),
        # Invalid
        ("invalid", None),
        # Decimal input
        (Decimal("4.99"), Decimal("4.99")),
        # Numeric types
        (10, Decimal("10.00")),
        (10.5, Decimal("10.50")),
    ],
)
def test_parse_price(raw: object, expected: Decimal | None) -> None:
    """Test parse_price with various inputs."""
    result = parse_price(raw)
    assert result == expected
    if expected is not None:
        # Verify it's always quantized to 2 decimal places
        assert result == result.quantize(Decimal("0.01"))
