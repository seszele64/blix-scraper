"""Date parsing utilities for the blix-scraper project.

This module provides date parsing, validation, and timezone conversion
functionality using the dateparser library.
"""

from datetime import datetime, timedelta, timezone
from typing import Final

import dateparser  # type: ignore[import-untyped]


class DateParseError(Exception):
    """Custom exception for date parsing failures.

    Attributes:
        input_string: The original input string that failed to parse.
        message: Explanation of the parsing failure.
    """

    def __init__(self, input_string: str, message: str) -> None:
        self.input_string = input_string
        self.message = message
        super().__init__(f"Failed to parse date '{input_string}': {message}")


class DateParser:
    """Service for parsing various date formats and expressions.

    Supports ISO dates, natural language dates ("today", "tomorrow"),
    date ranges, and special phrases like "this weekend", "next weekend",
    and "end of month".

    All parsed dates are returned in UTC timezone.

    Example:
        >>> parser = DateParser()
        >>> parser.parse("2024-01-15")
        datetime(2024, 1, 15, 0, 0, tzinfo=timezone.utc)
        >>> parser.parse("today")
        datetime(2024, ..., 0, 0, tzinfo=timezone.utc)
        >>> parser.parse_range("2024-01-01 to 2024-01-31")
        (datetime(2024, 1, 1, ..., datetime(2024, 1, 31, ...))
    """

    # Reasonable date bounds for validation
    MIN_YEAR: Final[int] = 2020
    MAX_YEAR: Final[int] = 2030
    MAX_FUTURE_DAYS: Final[int] = 365

    # Special phrase mappings
    _SPECIAL_PHRASES: Final[dict[str, str]] = {
        "today": "today",
        "tomorrow": "tomorrow",
        "yesterday": "yesterday",
        "this weekend": "this weekend",
        "next weekend": "next weekend",
        "end of month": "end of month",
    }

    def parse(self, date_string: str) -> datetime:
        """Parse a date string into a datetime object.

        Args:
            date_string: The date string to parse. Supports:
                - ISO format (YYYY-MM-DD)
                - Natural language ("today", "tomorrow", "yesterday")
                - Special phrases ("this weekend", "next weekend", "end of month")
                - Various date formats understood by dateparser

        Returns:
            datetime: The parsed date in UTC timezone.

        Raises:
            DateParseError: If the date string cannot be parsed.
        """
        if not date_string or not date_string.strip():
            raise DateParseError(date_string, "Empty date string")

        cleaned = date_string.strip().lower()

        # Handle special phrases first
        if cleaned in self._SPECIAL_PHRASES:
            return self._parse_special_phrase(cleaned)

        # Use dateparser for general cases
        parsed = dateparser.parse(
            date_string,
            settings={"TIMEZONE": "UTC", "RETURN_AS_TIMEZONE_AWARE": True},
        )

        if parsed is None:
            raise DateParseError(date_string, "Unable to parse date string")

        return self.to_utc(parsed)

    def _parse_special_phrase(self, phrase: str) -> datetime:
        """Parse special date phrases like "today", "tomorrow", etc.

        Args:
            phrase: The special phrase to parse.

        Returns:
            datetime: The parsed date in UTC timezone.

        Raises:
            DateParseError: If the phrase cannot be parsed.
        """
        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        match phrase:
            case "today":
                return today
            case "tomorrow":
                return today + timedelta(days=1)
            case "yesterday":
                return today - timedelta(days=1)
            case "this weekend":
                # Get Saturday (start) and Sunday (end) of current week
                return self._get_weekend(0)
            case "next weekend":
                # Get Saturday and Sunday of next week
                return self._get_weekend(1)
            case "end of month":
                return self._get_end_of_month()
            case _:
                raise DateParseError(phrase, f"Unknown special phrase: {phrase}")

    def _get_weekend(self, weeks_ahead: int) -> datetime:
        """Get the Saturday of the current or next weekend.

        Args:
            weeks_ahead: Number of weeks ahead (0 for this week, 1 for next).

        Returns:
            datetime: The Saturday of the specified weekend at midnight UTC.
        """
        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Calculate days until Saturday (0 = Monday, 5 = Saturday)
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0 and weeks_ahead > 0:
            days_until_saturday = 7

        saturday = today + timedelta(days=days_until_saturday + (weeks_ahead * 7))
        return saturday

    def _get_end_of_month(self) -> datetime:
        """Get the last day of the current month.

        Returns:
            datetime: The last day of the current month at midnight UTC.
        """
        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Get first day of next month
        if today.month == 12:
            first_of_next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            first_of_next_month = today.replace(month=today.month + 1, day=1)

        # Subtract one day to get last day of current month
        last_day = first_of_next_month - timedelta(days=1)
        return last_day.replace(hour=0, minute=0, second=0, microsecond=0)

    def parse_range(self, range_string: str) -> tuple[datetime, datetime]:
        """Parse a date range string into start and end datetime objects.

        Args:
            range_string: The date range string to parse. Supports:
                - "YYYY-MM-DD to YYYY-MM-DD"
                - "YYYY-MM-DD:YYYY-MM-DD"
                - "YYYY-MM-DD - YYYY-MM-DD"

        Returns:
            tuple[datetime, datetime]: A tuple of (start_date, end_date) in UTC.

        Raises:
            DateParseError: If the range string cannot be parsed or is invalid.
        """
        if not range_string or not range_string.strip():
            raise DateParseError(range_string, "Empty range string")

        cleaned = range_string.strip()

        # Try different separators (with and without spaces)
        separators = [" to ", " : ", " - ", ":", "to", "-"]
        parts: list[str] | None = None

        for sep in separators:
            if sep in cleaned:
                parts = cleaned.split(sep)
                break

        if parts is None or len(parts) != 2:
            raise DateParseError(
                range_string,
                "Invalid range format. Use 'YYYY-MM-DD to YYYY-MM-DD' or similar.",
            )

        start_date = self.parse(parts[0].strip())
        end_date = self.parse(parts[1].strip())

        if end_date < start_date:
            raise DateParseError(
                range_string,
                "End date must be after start date",
            )

        return (start_date, end_date)

    def validate(self, date: datetime) -> None:
        """Validate that a date is within reasonable bounds.

        Args:
            date: The datetime to validate.

        Raises:
            DateParseError: If the date is not within reasonable bounds.
        """
        # Ensure we're working with timezone-aware datetime
        if date.tzinfo is None:
            date = self.to_utc(date)

        # Check year bounds
        if date.year < self.MIN_YEAR:
            raise DateParseError(
                str(date.date()),
                f"Date too far in the past (before {self.MIN_YEAR})",
            )

        if date.year > self.MAX_YEAR:
            raise DateParseError(
                str(date.date()),
                f"Date too far in the future (after {self.MAX_YEAR})",
            )

        # Check future date bounds (if in current/future year)
        now = datetime.now(timezone.utc)
        if date.year >= now.year:
            days_ahead = (date - now).days
            if days_ahead > self.MAX_FUTURE_DAYS:
                raise DateParseError(
                    str(date.date()),
                    f"Date is more than {self.MAX_FUTURE_DAYS} days in the future",
                )

    def to_utc(self, date: datetime) -> datetime:
        """Convert a datetime to UTC timezone.

        Args:
            date: The datetime to convert. Can be naive or timezone-aware.

        Returns:
            datetime: The datetime in UTC timezone.
        """
        if date.tzinfo is None:
            # Naive datetime - assume local time and convert to UTC
            return date.replace(tzinfo=timezone.utc)
        else:
            # Timezone-aware - convert to UTC
            return date.astimezone(timezone.utc)
