"""Comprehensive unit tests for domain date filtering.

Tests cover:
- DateFilterOptions: Filter options for date-based filtering
- Leaflet.is_valid_in_range(): Range overlap checking
- Offer date methods: Delegation to leaflet
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.domain.date_filter import DateFilterOptions
from src.domain.entities import Leaflet, LeafletStatus, Offer

# ========== Fixtures ==========


@pytest.fixture
def leaflet_active() -> Leaflet:
    """Leaflet active from Jan 1 to Jan 31, 2025."""
    return Leaflet(
        leaflet_id=1,
        shop_slug="test-shop",
        name="Test Leaflet",
        cover_image_url="https://example.com/cover.jpg",
        url="https://example.com/leaflet/1",
        valid_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
        valid_until=datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.ACTIVE,
    )


@pytest.fixture
def leaflet_february() -> Leaflet:
    """Leaflet active from Feb 1 to Feb 28, 2025."""
    return Leaflet(
        leaflet_id=2,
        shop_slug="test-shop",
        name="February Leaflet",
        cover_image_url="https://example.com/cover2.jpg",
        url="https://example.com/leaflet/2",
        valid_from=datetime(2025, 2, 1, tzinfo=timezone.utc),
        valid_until=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.ACTIVE,
    )


@pytest.fixture
def offer_with_leaflet(leaflet_active) -> Offer:
    """Offer with attached leaflet."""
    return Offer(
        leaflet_id=1,
        name="Test Offer",
        price=Decimal("9.99"),
        image_url="https://example.com/offer.jpg",
        page_number=1,
        position_x=0.1,
        position_y=0.1,
        width=0.2,
        height=0.2,
        valid_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
        valid_until=datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
        leaflet=leaflet_active,
    )


@pytest.fixture
def offer_without_leaflet() -> Offer:
    """Offer without attached leaflet."""
    return Offer(
        leaflet_id=1,
        name="Test Offer",
        price=Decimal("9.99"),
        image_url="https://example.com/offer.jpg",
        page_number=1,
        position_x=0.1,
        position_y=0.1,
        width=0.2,
        height=0.2,
        valid_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
        valid_until=datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
    )


# ========== DateFilterOptions Tests ==========


@pytest.mark.unit
class TestDateFilterOptionsFields:
    """Test that all filter fields are Optional[datetime]."""

    def test_all_fields_default_to_none(self):
        """Test that all date filter fields default to None."""
        filter_opts = DateFilterOptions()
        assert filter_opts.active_on is None
        assert filter_opts.valid_from is None
        assert filter_opts.valid_until is None
        assert filter_opts.date_from is None
        assert filter_opts.date_to is None

    def test_fields_accept_datetime(self):
        """Test that all filter fields accept datetime values."""
        test_date = datetime(2025, 1, 15, tzinfo=timezone.utc)
        filter_opts = DateFilterOptions(
            active_on=test_date,
            valid_from=test_date,
            valid_until=test_date,
            date_from=test_date,
            date_to=test_date,
        )
        assert filter_opts.active_on == test_date
        assert filter_opts.valid_from == test_date
        assert filter_opts.valid_until == test_date
        assert filter_opts.date_from == test_date
        assert filter_opts.date_to == test_date

    def test_fields_accept_naive_datetime(self):
        """Test that fields accept naive datetime (treated as UTC)."""
        naive_date = datetime(2025, 1, 15)
        filter_opts = DateFilterOptions(
            active_on=naive_date,
            valid_from=naive_date,
            valid_until=naive_date,
            date_from=naive_date,
            date_to=naive_date,
        )
        assert filter_opts.active_on == naive_date
        assert filter_opts.valid_from == naive_date
        assert filter_opts.valid_until == naive_date
        assert filter_opts.date_from == naive_date
        assert filter_opts.date_to == naive_date


@pytest.mark.unit
class TestDateFilterOptionsHasDateFilter:
    """Test has_date_filter() method."""

    def test_returns_false_when_no_filters_set(self):
        """Test has_date_filter() returns False when no filters set."""
        filter_opts = DateFilterOptions()
        assert filter_opts.has_date_filter() is False

    def test_returns_true_when_active_on_set(self):
        """Test has_date_filter() returns True when active_on is set."""
        filter_opts = DateFilterOptions(active_on=datetime(2025, 1, 15))
        assert filter_opts.has_date_filter() is True

    def test_returns_true_when_valid_from_set(self):
        """Test has_date_filter() returns True when valid_from is set."""
        filter_opts = DateFilterOptions(valid_from=datetime(2025, 1, 1))
        assert filter_opts.has_date_filter() is True

    def test_returns_true_when_valid_until_set(self):
        """Test has_date_filter() returns True when valid_until is set."""
        filter_opts = DateFilterOptions(valid_until=datetime(2025, 1, 31))
        assert filter_opts.has_date_filter() is True

    def test_returns_true_when_date_from_set(self):
        """Test has_date_filter() returns True when date_from is set."""
        filter_opts = DateFilterOptions(date_from=datetime(2025, 1, 1))
        assert filter_opts.has_date_filter() is True

    def test_returns_true_when_date_to_set(self):
        """Test has_date_filter() returns True when date_to is set."""
        filter_opts = DateFilterOptions(date_to=datetime(2025, 1, 31))
        assert filter_opts.has_date_filter() is True

    def test_returns_true_when_multiple_filters_set(self):
        """Test has_date_filter() returns True when multiple filters set."""
        filter_opts = DateFilterOptions(
            date_from=datetime(2025, 1, 1),
            date_to=datetime(2025, 1, 31),
        )
        assert filter_opts.has_date_filter() is True


@pytest.mark.unit
class TestDateFilterOptionsToPredicate:
    """Test to_predicate() method."""

    # ========== No Filters Tests ==========

    def test_returns_true_for_all_when_no_filters(self, leaflet_active):
        """Test to_predicate() returns True for all when no filters set."""
        filter_opts = DateFilterOptions()
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is True

    # ========== active_on Filter Tests ==========

    def test_predicate_with_active_on_within_range(self, leaflet_active):
        """Test to_predicate() with active_on filter when date is within range."""
        filter_opts = DateFilterOptions(active_on=datetime(2025, 1, 15, tzinfo=timezone.utc))
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is True

    def test_predicate_with_active_on_before_range(self, leaflet_active):
        """Test to_predicate() with active_on filter when date is before range."""
        filter_opts = DateFilterOptions(active_on=datetime(2024, 12, 15, tzinfo=timezone.utc))
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_with_active_on_after_range(self, leaflet_active):
        """Test to_predicate() with active_on filter when date is after range."""
        filter_opts = DateFilterOptions(active_on=datetime(2025, 2, 15, tzinfo=timezone.utc))
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_with_active_on_at_start_boundary(self, leaflet_active):
        """Test to_predicate() with active_on at exact start boundary."""
        filter_opts = DateFilterOptions(active_on=datetime(2025, 1, 1, tzinfo=timezone.utc))
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is True

    def test_predicate_with_active_on_at_end_boundary(self, leaflet_active):
        """Test to_predicate() with active_on at exact end boundary."""
        filter_opts = DateFilterOptions(
            active_on=datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is True

    def test_predicate_with_active_on_naive_datetime(self, leaflet_active):
        """Test to_predicate() with active_on using naive datetime."""
        # Naive datetime should be treated as UTC
        filter_opts = DateFilterOptions(active_on=datetime(2025, 1, 15))
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is True

    def test_predicate_with_active_on_entity_without_is_valid_on(self):
        """Test to_predicate() falls back to valid_from/valid_until check."""

        # Create a simple object with valid_from and valid_until
        class SimpleEntity:
            valid_from = datetime(2025, 1, 1, tzinfo=timezone.utc)
            valid_until = datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)

        entity = SimpleEntity()
        filter_opts = DateFilterOptions(active_on=datetime(2025, 1, 15, tzinfo=timezone.utc))
        predicate = filter_opts.to_predicate()
        assert predicate(entity) is True

    def test_predicate_with_active_on_entity_missing_dates(self):
        """Test to_predicate() returns False for entity without date attributes."""

        class NoDatesEntity:
            name = "test"

        entity = NoDatesEntity()
        filter_opts = DateFilterOptions(active_on=datetime(2025, 1, 15, tzinfo=timezone.utc))
        predicate = filter_opts.to_predicate()
        assert predicate(entity) is False

    # ========== date_from/date_to Range Filter Tests ==========

    def test_predicate_with_date_range_full_overlap(self, leaflet_active):
        """Test to_predicate() with range that fully contains leaflet."""
        filter_opts = DateFilterOptions(
            date_from=datetime(2024, 12, 1, tzinfo=timezone.utc),
            date_to=datetime(2025, 2, 28, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is True

    def test_predicate_with_date_range_partial_start(self, leaflet_active):
        """Test to_predicate() with range that starts inside leaflet (partial overlap at end)."""
        # Range: Jan 15 to Feb 28 - leaflet starts before range but ends within range
        # The predicate checks if entity.valid_from >= date_from
        # leaflet.valid_from (Jan 1) < date_from (Jan 15) -> returns False
        # This is because the filter expects entities that START on or after date_from
        filter_opts = DateFilterOptions(
            date_from=datetime(2025, 1, 15, tzinfo=timezone.utc),
            date_to=datetime(2025, 2, 28, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        # Entity starts before the range, so it doesn't match
        assert predicate(leaflet_active) is False

    def test_predicate_with_date_range_partial_end(self, leaflet_active):
        """Test to_predicate() with range that ends inside leaflet (partial overlap at start)."""
        # Range: Dec 1 to Jan 15 - leaflet starts within range but ends after range
        # leaflet.valid_until (Jan 31) > date_to (Jan 15) -> returns False
        filter_opts = DateFilterOptions(
            date_from=datetime(2024, 12, 1, tzinfo=timezone.utc),
            date_to=datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        # Entity ends after the range, so it doesn't match
        assert predicate(leaflet_active) is False

    def test_predicate_with_date_range_no_overlap_before(self, leaflet_active):
        """Test to_predicate() with range completely before leaflet."""
        filter_opts = DateFilterOptions(
            date_from=datetime(2024, 6, 1, tzinfo=timezone.utc),
            date_to=datetime(2024, 6, 30, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_with_date_range_no_overlap_after(self, leaflet_active):
        """Test to_predicate() with range completely after leaflet."""
        filter_opts = DateFilterOptions(
            date_from=datetime(2025, 6, 1, tzinfo=timezone.utc),
            date_to=datetime(2025, 6, 30, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_with_date_range_exact_match(self, leaflet_active):
        """Test to_predicate() with range exactly matching leaflet dates."""
        filter_opts = DateFilterOptions(
            date_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            date_to=datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is True

    def test_predicate_with_date_range_only_from(self, leaflet_active):
        """Test to_predicate() with only date_from set."""
        # date_from means the entity must start on or after this date
        # leaflet.valid_from (Jan 1) < date_from (Jan 15) -> returns False
        filter_opts = DateFilterOptions(
            date_from=datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_with_date_range_only_to(self, leaflet_active):
        """Test to_predicate() with only date_to set."""
        # date_to means the entity must end on or before this date
        # leaflet.valid_until (Jan 31) > date_to (Jan 15) -> returns False
        filter_opts = DateFilterOptions(
            date_to=datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_with_date_range_entity_missing_dates(self):
        """Test to_predicate() returns False for entity without valid_from/valid_until."""

        class NoDatesEntity:
            name = "test"

        entity = NoDatesEntity()
        filter_opts = DateFilterOptions(
            date_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            date_to=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(entity) is False

    # ========== valid_from/valid_until Alias Tests ==========

    def test_predicate_with_valid_from_alias(self, leaflet_active):
        """Test to_predicate() using valid_from alias (same as date_from)."""
        # valid_from works like date_from - entity must start on or after this date
        # leaflet.valid_from (Jan 1) < valid_from (Jan 15) -> returns False
        filter_opts = DateFilterOptions(
            valid_from=datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_with_valid_until_alias(self, leaflet_active):
        """Test to_predicate() using valid_until alias (same as date_to)."""
        # valid_until works like date_to - entity must end on or before this date
        # leaflet.valid_until (Jan 31) > valid_until (Jan 15) -> returns False
        filter_opts = DateFilterOptions(
            valid_until=datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_with_valid_range(self, leaflet_active):
        """Test to_predicate() with valid_from and valid_until."""
        # valid_from = Jan 15, valid_until = Feb 15
        # leaflet.valid_from (Jan 1) < valid_from (Jan 15) -> returns False
        filter_opts = DateFilterOptions(
            valid_from=datetime(2025, 1, 15, tzinfo=timezone.utc),
            valid_until=datetime(2025, 2, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_date_from_overrides_valid_from(self, leaflet_active):
        """Test that date_from takes precedence over valid_from."""
        filter_opts = DateFilterOptions(
            valid_from=datetime(2025, 1, 1, tzinfo=timezone.utc),  # Would include leaflet
            date_from=datetime(2025, 2, 1, tzinfo=timezone.utc),  # Would exclude leaflet
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    def test_predicate_date_to_overrides_valid_until(self, leaflet_active):
        """Test that date_to takes precedence over valid_until."""
        filter_opts = DateFilterOptions(
            valid_until=datetime(2025, 2, 28, tzinfo=timezone.utc),  # Would include leaflet
            date_to=datetime(2025, 1, 15, tzinfo=timezone.utc),  # Would exclude leaflet
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_active) is False

    # ========== Valid Matching Cases ==========

    def test_predicate_with_date_from_entity_starts_after(self, leaflet_february):
        """Test predicate matches when entity starts after date_from."""
        # Leaflet: Feb 1 to Feb 28
        # Filter: date_from = Jan 15
        # leaflet.valid_from (Feb 1) >= date_from (Jan 15) -> True
        filter_opts = DateFilterOptions(
            date_from=datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_february) is True

    def test_predicate_with_date_to_entity_ends_before(self, leaflet_february):
        """Test predicate matches when entity ends before date_to."""
        # Leaflet: Feb 1 to Feb 28
        # Filter: date_to = Mar 15
        # leaflet.valid_until (Feb 28) <= date_to (Mar 15) -> True
        filter_opts = DateFilterOptions(
            date_to=datetime(2025, 3, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_february) is True

    def test_predicate_with_valid_from_and_until_within_range(self, leaflet_february):
        """Test predicate with both valid_from and valid_until within range."""
        # Leaflet: Feb 1 to Feb 28
        # Filter: valid_from = Jan 15, valid_until = Mar 15
        # Both conditions satisfied -> True
        filter_opts = DateFilterOptions(
            valid_from=datetime(2025, 1, 15, tzinfo=timezone.utc),
            valid_until=datetime(2025, 3, 15, tzinfo=timezone.utc),
        )
        predicate = filter_opts.to_predicate()
        assert predicate(leaflet_february) is True


# ========== Leaflet.is_valid_in_range() Tests ==========


@pytest.mark.unit
class TestLeafletIsValidInRange:
    """Test Leaflet.is_valid_in_range() method."""

    def test_returns_true_when_range_fully_overlaps(self, leaflet_active):
        """Test returns True when filter range fully contains leaflet."""
        # Range from Dec 15 to Feb 15 fully contains Jan 1-31 leaflet
        result = leaflet_active.is_valid_in_range(
            datetime(2024, 12, 15, tzinfo=timezone.utc),
            datetime(2025, 2, 15, tzinfo=timezone.utc),
        )
        assert result is True

    def test_returns_true_when_range_partially_overlaps_start(self, leaflet_active):
        """Test returns True when range overlaps at the start of leaflet."""
        # Range from Jan 15 to Feb 15 overlaps Jan 15-31
        result = leaflet_active.is_valid_in_range(
            datetime(2025, 1, 15, tzinfo=timezone.utc),
            datetime(2025, 2, 15, tzinfo=timezone.utc),
        )
        assert result is True

    def test_returns_true_when_range_partially_overlaps_end(self, leaflet_active):
        """Test returns True when range overlaps at the end of leaflet."""
        # Range from Dec 15 to Jan 15 overlaps Jan 1-15
        result = leaflet_active.is_valid_in_range(
            datetime(2024, 12, 15, tzinfo=timezone.utc),
            datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        assert result is True

    def test_returns_false_when_no_overlap_before(self, leaflet_active):
        """Test returns False when range is completely before leaflet."""
        # Range from Oct 1 to Nov 30 is completely before Jan 1-31
        result = leaflet_active.is_valid_in_range(
            datetime(2024, 10, 1, tzinfo=timezone.utc),
            datetime(2024, 11, 30, tzinfo=timezone.utc),
        )
        assert result is False

    def test_returns_false_when_no_overlap_after(self, leaflet_active):
        """Test returns False when range is completely after leaflet."""
        # Range from Mar 1 to Apr 30 is completely after Jan 1-31
        result = leaflet_active.is_valid_in_range(
            datetime(2025, 3, 1, tzinfo=timezone.utc),
            datetime(2025, 4, 30, tzinfo=timezone.utc),
        )
        assert result is False

    def test_edge_case_exact_start_boundary(self, leaflet_active):
        """Test edge case: range starts exactly when leaflet starts."""
        # Range starts exactly on leaflet valid_from
        result = leaflet_active.is_valid_in_range(
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        assert result is True

    def test_edge_case_exact_end_boundary(self, leaflet_active):
        """Test edge case: range ends exactly when leaflet ends."""
        # Range ends exactly on leaflet valid_until
        result = leaflet_active.is_valid_in_range(
            datetime(2025, 1, 15, tzinfo=timezone.utc),
            datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
        )
        assert result is True

    def test_edge_case_exact_match(self, leaflet_active):
        """Test edge case: range exactly matches leaflet validity."""
        result = leaflet_active.is_valid_in_range(
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
        )
        assert result is True

    def test_with_naive_datetime_range(self, leaflet_active):
        """Test with naive datetime range (treated as UTC)."""
        result = leaflet_active.is_valid_in_range(
            datetime(2025, 1, 15),  # naive
            datetime(2025, 2, 15),  # naive
        )
        assert result is True

    def test_with_naive_leaflet_dates(self):
        """Test with naive datetime in leaflet (treated as UTC)."""
        leaflet = Leaflet(
            leaflet_id=1,
            shop_slug="test-shop",
            name="Test Leaflet",
            cover_image_url="https://example.com/cover.jpg",
            url="https://example.com/leaflet/1",
            valid_from=datetime(2025, 1, 1),  # naive
            valid_until=datetime(2025, 1, 31, 23, 59, 59),  # naive
            status=LeafletStatus.ACTIVE,
        )
        result = leaflet.is_valid_in_range(
            datetime(2025, 1, 15, tzinfo=timezone.utc),
            datetime(2025, 2, 15, tzinfo=timezone.utc),
        )
        assert result is True


# ========== Offer Date Methods Tests ==========


@pytest.mark.unit
class TestOfferIsValidOn:
    """Test Offer.is_valid_on() method."""

    def test_delegates_to_leaflet_when_valid_on_date(self, offer_with_leaflet):
        """Test is_valid_on delegates to leaflet and returns True when valid."""
        result = offer_with_leaflet.is_valid_on(datetime(2025, 1, 15, tzinfo=timezone.utc))
        assert result is True

    def test_delegates_to_leaflet_when_not_valid_on_date(self, offer_with_leaflet):
        """Test is_valid_on delegates to leaflet and returns False when not valid."""
        result = offer_with_leaflet.is_valid_on(datetime(2025, 2, 15, tzinfo=timezone.utc))
        assert result is False

    def test_returns_false_when_no_leaflet_attached(self, offer_without_leaflet):
        """Test is_valid_on returns False when no leaflet attached."""
        result = offer_without_leaflet.is_valid_on(datetime(2025, 1, 15, tzinfo=timezone.utc))
        assert result is False


@pytest.mark.unit
class TestOfferIsValidInRange:
    """Test Offer.is_valid_in_range() method."""

    def test_delegates_to_leaflet_when_range_overlaps(self, offer_with_leaflet):
        """Test is_valid_in_range delegates to leaflet and returns True on overlap."""
        result = offer_with_leaflet.is_valid_in_range(
            datetime(2024, 12, 15, tzinfo=timezone.utc),
            datetime(2025, 2, 15, tzinfo=timezone.utc),
        )
        assert result is True

    def test_delegates_to_leaflet_when_range_does_not_overlap(self, offer_with_leaflet):
        """Test is_valid_in_range delegates to leaflet and returns False on no overlap."""
        result = offer_with_leaflet.is_valid_in_range(
            datetime(2025, 6, 1, tzinfo=timezone.utc),
            datetime(2025, 6, 30, tzinfo=timezone.utc),
        )
        assert result is False

    def test_returns_false_when_no_leaflet_attached(self, offer_without_leaflet):
        """Test is_valid_in_range returns False when no leaflet attached."""
        result = offer_without_leaflet.is_valid_in_range(
            datetime(2025, 1, 15, tzinfo=timezone.utc),
            datetime(2025, 2, 15, tzinfo=timezone.utc),
        )
        assert result is False
