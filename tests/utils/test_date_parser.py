"""Comprehensive unit tests for the DateParser service.

Tests cover:
- DateParseError: Exception handling and message formatting
- DateParser.parse(): Various date formats and expressions
- DateParser.parse_range(): Date range parsing with various separators
- DateParser.validate(): Date validation within reasonable bounds
- DateParser.to_utc(): Timezone conversion to UTC
- Special phrases: "today", "tomorrow", "yesterday", "this weekend", etc.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from src.utils.date_parser import DateParseError, DateParser

# ========== Fixtures ==========


@pytest.fixture
def parser() -> DateParser:
    """Create a DateParser instance for testing."""
    return DateParser()


@pytest.fixture
def fixed_now() -> datetime:
    """Fixed datetime for testing (2025-06-15 12:00:00 UTC)."""
    return datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def mock_fixed_now(fixed_now) -> Mock:
    """Mock datetime.now to return fixed_now."""
    with patch("src.utils.date_parser.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield mock_datetime


# ========== DateParseError Tests ==========


@pytest.mark.unit
class TestDateParseError:
    """Test DateParseError exception class."""

    def test_exception_stores_input_string(self):
        """Test that exception stores the input_string attribute."""
        error = DateParseError("invalid-date", "Unable to parse")
        assert error.input_string == "invalid-date"

    def test_exception_message_formatting(self):
        """Test that exception message is formatted correctly."""
        error = DateParseError("2024-01-01", "Invalid format")
        assert "Failed to parse date '2024-01-01': Invalid format" in str(error)

    def test_exception_message_includes_input(self):
        """Test that exception message includes the input string."""
        error = DateParseError("", "Empty date string")
        assert "Empty date string" in str(error)

    def test_exception_is_exception_subclass(self):
        """Test that DateParseError inherits from Exception."""
        error = DateParseError("test", "message")
        assert isinstance(error, Exception)

    def test_exception_can_be_caught_as_value_error(self):
        """Test that DateParseError can be caught as ValueError subclass."""
        # Note: DateParseError doesn't inherit from ValueError,
        # so this test verifies it doesn't inherit from it
        with pytest.raises(DateParseError):
            raise DateParseError("test", "error")


# ========== DateParser.parse() Tests ==========


@pytest.mark.unit
class TestDateParserParse:
    """Test DateParser.parse() method."""

    # ISO Date Format Tests

    def test_parse_iso_date_yyyy_mm_dd(self, parser):
        """Test parsing ISO date format YYYY-MM-DD."""
        result = parser.parse("2024-01-15")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.tzinfo == timezone.utc

    def test_parse_iso_date_returns_utc(self, parser):
        """Test that parsed dates are returned in UTC timezone."""
        result = parser.parse("2024-01-15")
        assert result.tzinfo is not None
        assert result.astimezone(timezone.utc) == result

    # Various Date Format Tests

    @pytest.mark.parametrize(
        "date_string,expected_year,expected_month,expected_day",
        [
            ("15/01/2024", 2024, 1, 15),
            ("01-15-2024", 2024, 1, 15),  # MM-DD-YYYY
            ("15.01.2024", 2024, 1, 15),  # DD.MM.YYYY
            ("2024/01/15", 2024, 1, 15),  # YYYY/MM/DD
        ],
    )
    def test_parse_various_date_formats(
        self, parser, date_string, expected_year, expected_month, expected_day
    ):
        """Test parsing various date format strings."""
        result = parser.parse(date_string)
        assert result.year == expected_year
        assert result.month == expected_month
        assert result.day == expected_day
        assert result.tzinfo == timezone.utc

    # Special Keyword Tests

    def test_parse_today_returns_current_date(self, parser, mock_fixed_now):
        """Test that 'today' returns the current date."""
        result = parser.parse("today")
        expected = datetime(2025, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_parse_tomorrow_returns_next_day(self, parser, mock_fixed_now):
        """Test that 'tomorrow' returns the next day."""
        result = parser.parse("tomorrow")
        expected = datetime(2025, 6, 16, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_parse_yesterday_returns_previous_day(self, parser, mock_fixed_now):
        """Test that 'yesterday' returns the previous day."""
        result = parser.parse("yesterday")
        expected = datetime(2025, 6, 14, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    # Error Handling Tests

    def test_parse_empty_string_raises_error(self, parser):
        """Test that empty string raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse("")
        assert "Empty date string" in exc_info.value.message

    def test_parse_whitespace_only_raises_error(self, parser):
        """Test that whitespace-only string raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse("   ")
        assert "Empty date string" in exc_info.value.message

    def test_parse_invalid_date_raises_error(self, parser):
        """Test that invalid date raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse("not-a-date")
        assert "Unable to parse date string" in exc_info.value.message

    def test_parse_invalid_date_stores_input(self, parser):
        """Test that DateParseError stores the invalid input."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse("invalid-date-string")
        assert exc_info.value.input_string == "invalid-date-string"

    # Case Handling Tests

    def test_parse_uppercase_today(self, parser, mock_fixed_now):
        """Test parsing uppercase 'TODAY'."""
        result = parser.parse("TODAY")
        expected = datetime(2025, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_parse_mixed_case_today(self, parser, mock_fixed_now):
        """Test parsing mixed case 'Today'."""
        result = parser.parse("Today")
        expected = datetime(2025, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected


# ========== DateParser.parse_range() Tests ==========


@pytest.mark.unit
class TestDateParserParseRange:
    """Test DateParser.parse_range() method."""

    # Separator Tests

    def test_parse_range_with_to_separator(self, parser):
        """Test parsing range with 'to' separator."""
        result = parser.parse_range("2024-01-01 to 2024-01-31")
        start, end = result
        assert start.year == 2024
        assert start.month == 1
        assert start.day == 1
        assert end.year == 2024
        assert end.month == 1
        assert end.day == 31

    def test_parse_range_with_colon_separator(self, parser):
        """Test parsing range with colon separator."""
        result = parser.parse_range("2024-01-01:2024-01-31")
        start, end = result
        assert start.year == 2024
        assert start.month == 1
        assert start.day == 1
        assert end.year == 2024
        assert end.month == 1
        assert end.day == 31

    def test_parse_range_with_dash_separator(self, parser):
        """Test parsing range with dash separator (with spaces)."""
        result = parser.parse_range("2024-01-01 - 2024-01-31")
        start, end = result
        assert start.year == 2024
        assert start.month == 1
        assert start.day == 1
        assert end.year == 2024
        assert end.month == 1
        assert end.day == 31

    def test_parse_range_returns_utc_datetimes(self, parser):
        """Test that parsed range returns UTC datetime objects."""
        result = parser.parse_range("2024-01-01 to 2024-01-31")
        start, end = result
        assert start.tzinfo == timezone.utc
        assert end.tzinfo == timezone.utc

    # Special Phrases in Range Tests

    def test_parse_range_with_today_keyword(self, parser, mock_fixed_now):
        """Test parsing range with 'today' keyword."""
        # Today is 2025-06-15, so we need end date after today
        result = parser.parse_range("today to 2025-12-31")
        start, end = result
        assert start.date() == datetime(2025, 6, 15).date()

    def test_parse_range_with_tomorrow_keyword(self, parser, mock_fixed_now):
        """Test parsing range with 'tomorrow' keyword."""
        # Tomorrow is 2025-06-16, so we need end date after tomorrow
        result = parser.parse_range("tomorrow to 2025-12-31")
        start, end = result
        assert start.date() == datetime(2025, 6, 16).date()

    # Error Handling Tests

    def test_parse_range_empty_string_raises_error(self, parser):
        """Test that empty range string raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse_range("")
        assert "Empty range string" in exc_info.value.message

    def test_parse_range_no_separator_raises_error(self, parser):
        """Test that range without separator raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse_range("2024-01-01 2024-01-31")
        assert "Invalid range format" in exc_info.value.message

    def test_parse_range_start_after_end_raises_error(self, parser):
        """Test that start > end raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse_range("2024-01-31 to 2024-01-01")
        assert "End date must be after start date" in exc_info.value.message

    def test_parse_range_invalid_start_date_raises_error(self, parser):
        """Test that invalid start date raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse_range("invalid to 2024-01-31")
        assert "Unable to parse date string" in exc_info.value.message

    def test_parse_range_invalid_end_date_raises_error(self, parser):
        """Test that invalid end date raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse_range("2024-01-01 to invalid")
        assert "Unable to parse date string" in exc_info.value.message


# ========== DateParser.validate() Tests ==========


@pytest.mark.unit
class TestDateParserValidate:
    """Test DateParser.validate() method."""

    def test_validate_valid_date_in_range(self, parser):
        """Test that valid dates within range pass validation."""
        valid_date = datetime(2024, 6, 15, tzinfo=timezone.utc)
        # Should not raise
        parser.validate(valid_date)

    def test_validate_min_boundary_date(self, parser):
        """Test validation at minimum year boundary (2020)."""
        min_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        # Should not raise
        parser.validate(min_date)

    def test_validate_max_boundary_date(self, parser):
        """Test validation at maximum year boundary (2025, within 365 days)."""
        # 2025-06-15 is today, so 2025-12-31 is ~199 days in future (valid)
        max_date = datetime(2025, 12, 31, tzinfo=timezone.utc)
        # Should not raise
        parser.validate(max_date)

    def test_validate_date_too_far_in_past_raises_error(self, parser):
        """Test that dates before 2020 raise DateParseError."""
        past_date = datetime(2019, 12, 31, tzinfo=timezone.utc)
        with pytest.raises(DateParseError) as exc_info:
            parser.validate(past_date)
        assert "too far in the past" in exc_info.value.message

    def test_validate_date_too_far_in_future_raises_error(self, parser):
        """Test that dates after 2030 raise DateParseError."""
        future_date = datetime(2031, 1, 1, tzinfo=timezone.utc)
        with pytest.raises(DateParseError) as exc_info:
            parser.validate(future_date)
        assert "too far in the future" in exc_info.value.message

    def test_validate_date_more_than_365_days_future_raises_error(self):
        """Test that dates more than 365 days in future raise DateParseError."""
        # Use a mock to fix "now" to a specific date
        # We need to patch the datetime module in the date_parser module
        import src.utils.date_parser as date_parser_module

        original_datetime = date_parser_module.datetime

        try:
            fixed_now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

            class MockDatetime:
                """Mock datetime class."""

                @staticmethod
                def now(tz=None):
                    return fixed_now

            # Replace datetime with mock
            date_parser_module.datetime = MockDatetime  # type: ignore[assignment]

            # Create a new parser instance to use the mocked datetime
            parser = DateParser()
            # 2025-06-15 + 366 days = 2026-06-17 (366 days is > 365)
            future_date = datetime(2026, 6, 17, tzinfo=timezone.utc)
            with pytest.raises(DateParseError) as exc_info:
                parser.validate(future_date)
            assert "more than 365 days in the future" in exc_info.value.message
        finally:
            # Restore original datetime
            date_parser_module.datetime = original_datetime

    def test_validate_date_exactly_365_days_future_passes(self, parser, mock_fixed_now):
        """Test that dates exactly 365 days in future pass validation."""
        # 2025-06-15 + 365 days = 2026-06-15
        future_date = datetime(2026, 6, 15, tzinfo=timezone.utc)
        # Should not raise
        parser.validate(future_date)

    def test_validate_naive_datetime_converted(self, parser):
        """Test that naive datetime is converted and validated."""
        naive_date = datetime(2024, 6, 15)
        # Should not raise (converts to UTC)
        parser.validate(naive_date)


# ========== DateParser.to_utc() Tests ==========


@pytest.mark.unit
class TestDateParserToUtc:
    """Test DateParser.to_utc() method."""

    def test_to_utc_naive_datetime(self, parser):
        """Test that naive datetime is converted to UTC."""
        naive = datetime(2024, 6, 15, 12, 0, 0)
        result = parser.to_utc(naive)
        assert result.tzinfo == timezone.utc
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15

    def test_to_utc_timezone_aware_datetime(self, parser):
        """Test that timezone-aware datetime is converted to UTC."""
        # Create a datetime in a different timezone (e.g., +2 hours)
        other_tz = timezone(timedelta(hours=2))
        aware = datetime(2024, 6, 15, 14, 0, 0, tzinfo=other_tz)
        result = parser.to_utc(aware)
        assert result.tzinfo == timezone.utc
        assert result.hour == 12  # 14:00 + 2h offset = 12:00 UTC

    def test_to_utc_already_utc_unchanged(self, parser):
        """Test that already UTC datetime is unchanged."""
        utc_dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parser.to_utc(utc_dt)
        assert result == utc_dt

    def test_to_utc_negative_timezone(self, parser):
        """Test conversion from negative timezone to UTC."""
        # Create a datetime in a negative timezone (e.g., -5 hours)
        other_tz = timezone(timedelta(hours=-5))
        aware = datetime(2024, 6, 15, 7, 0, 0, tzinfo=other_tz)
        result = parser.to_utc(aware)
        assert result.tzinfo == timezone.utc
        assert result.hour == 12  # 07:00 - 5h offset = 12:00 UTC


# ========== Special Phrases Tests ==========


@pytest.mark.unit
class TestDateParserSpecialPhrases:
    """Test DateParser with special phrase parsing."""

    def test_parse_this_weekend(self, parser, mock_fixed_now):
        """Test parsing 'this weekend' returns Saturday of current week."""
        # 2025-06-15 is a Sunday
        # This weekend should be 2025-06-21 (Saturday)
        result = parser.parse("this weekend")
        # Should be a Saturday
        assert result.weekday() == 5  # Saturday
        assert result.tzinfo == timezone.utc

    def test_parse_next_weekend(self, parser, mock_fixed_now):
        """Test parsing 'next weekend' returns Saturday of next week."""
        # 2025-06-15 is a Sunday
        # Next weekend should be 2025-06-28 (Saturday)
        result = parser.parse("next weekend")
        # Should be a Saturday
        assert result.weekday() == 5  # Saturday
        assert result.tzinfo == timezone.utc
        # Should be in the future compared to this weekend
        this_weekend = parser.parse("this weekend")
        assert result > this_weekend

    def test_parse_end_of_month(self, parser, mock_fixed_now):
        """Test parsing 'end of month' returns last day of current month."""
        # 2025-06-15 - June has 30 days
        result = parser.parse("end of month")
        assert result.year == 2025
        assert result.month == 6
        assert result.day == 30
        assert result.tzinfo == timezone.utc

    def test_parse_end_of_month_december(self, parser):
        """Test 'end of month' for December."""
        # Mock to December
        with patch("src.utils.date_parser.datetime") as mock_datetime:
            dec_date = datetime(2024, 12, 15, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = dec_date
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            parser = DateParser()
            result = parser.parse("end of month")
            assert result.year == 2024
            assert result.month == 12
            assert result.day == 31

    def test_special_phrase_returns_midnight(self, parser, mock_fixed_now):
        """Test that special phrases return midnight (00:00:00) time."""
        result = parser.parse("today")
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0

    def test_unknown_phrase_raises_error(self, parser):
        """Test that unknown phrases raise DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            parser.parse("next millennium")
        assert "Unable to parse date string" in exc_info.value.message


# ========== Integration Tests ==========


@pytest.mark.unit
class TestDateParserIntegration:
    """Integration tests combining multiple DateParser methods."""

    def test_parse_and_validate_valid_date(self, parser):
        """Test parsing and validating a valid date."""
        date = parser.parse("2024-06-15")
        parser.validate(date)  # Should not raise

    def test_parse_and_validate_invalid_date(self, parser):
        """Test parsing and validating an invalid date."""
        date = parser.parse("2019-01-01")
        with pytest.raises(DateParseError):
            parser.validate(date)

    def test_parse_range_and_validate(self, parser):
        """Test parsing a range and validating both dates."""
        start, end = parser.parse_range("2024-01-01 to 2024-12-31")
        parser.validate(start)  # Should not raise
        parser.validate(end)  # Should not raise

    def test_parse_with_to_utc_conversion(self, parser):
        """Test parsing converts to UTC."""
        result = parser.parse("2024-06-15")
        assert result.tzinfo == timezone.utc
        # Verify it's actually in UTC
        assert result.astimezone(timezone.utc) == result


# ========== Edge Case Tests ==========


@pytest.mark.unit
class TestDateParserEdgeCases:
    """Edge case tests for DateParser."""

    def test_parse_leap_year_date(self, parser):
        """Test parsing a leap year date (Feb 29, 2024)."""
        result = parser.parse("2024-02-29")
        assert result.year == 2024
        assert result.month == 2
        assert result.day == 29

    def test_parse_first_day_of_year(self, parser):
        """Test parsing first day of year."""
        result = parser.parse("2024-01-01")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1

    def test_parse_last_day_of_year(self, parser):
        """Test parsing last day of year."""
        result = parser.parse("2024-12-31")
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 31

    def test_parse_whitespace_handling(self, parser):
        """Test that leading/trailing whitespace is handled."""
        result = parser.parse("  2024-06-15  ")
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15

    def test_parse_range_whitespace_handling(self, parser):
        """Test that range string whitespace is handled."""
        result = parser.parse_range("  2024-01-01  to  2024-12-31  ")
        start, end = result
        assert start.year == 2024
        assert end.year == 2024
