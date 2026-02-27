"""Tests for DateFilteredJSONStorage."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from src.domain.date_filter import DateFilterOptions
from src.domain.entities import Leaflet, LeafletStatus
from src.storage.date_filtered_storage import DateFilteredJSONStorage

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def leaflet_storage(tmp_path) -> DateFilteredJSONStorage[Leaflet]:
    """Create date-filtered leaflet storage instance with tmp_path."""
    return DateFilteredJSONStorage(tmp_path, Leaflet)


@pytest.fixture
def leaflet_january() -> Leaflet:
    """Leaflet valid in January 2025."""
    return Leaflet(
        leaflet_id=1,
        shop_slug="biedronka",
        name="January Sale",
        cover_image_url="https://example.com/leaflet1.jpg",
        url="https://blix.pl/sklep/biedronka/gazetka/1/",
        valid_from=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.ACTIVE,
        page_count=12,
    )


@pytest.fixture
def leaflet_february() -> Leaflet:
    """Leaflet valid in February 2025."""
    return Leaflet(
        leaflet_id=2,
        shop_slug="biedronka",
        name="February Promotion",
        cover_image_url="https://example.com/leaflet2.jpg",
        url="https://blix.pl/sklep/biedronka/gazetka/2/",
        valid_from=datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.ACTIVE,
        page_count=8,
    )


@pytest.fixture
def leaflet_march() -> Leaflet:
    """Leaflet valid in March 2025."""
    return Leaflet(
        leaflet_id=3,
        shop_slug="lidl",
        name="March Offers",
        cover_image_url="https://example.com/leaflet3.jpg",
        url="https://blix.pl/sklep/lidl/gazetka/3/",
        valid_from=datetime(2025, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2025, 3, 31, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.ACTIVE,
        page_count=16,
    )


@pytest.fixture
def leaflet_jan_feb() -> Leaflet:
    """Leaflet valid from January to February (spans two months)."""
    return Leaflet(
        leaflet_id=4,
        shop_slug="biedronka",
        name="Winter Sale",
        cover_image_url="https://example.com/leaflet4.jpg",
        url="https://blix.pl/sklep/biedronka/gazetka/4/",
        valid_from=datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2025, 2, 15, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.ACTIVE,
        page_count=10,
    )


@pytest.fixture
def leaflet_feb_mar() -> Leaflet:
    """Leaflet valid from February to March (spans two months)."""
    return Leaflet(
        leaflet_id=5,
        shop_slug="kaufland",
        name="Spring Preview",
        cover_image_url="https://example.com/leaflet5.jpg",
        url="https://blix.pl/sklep/kaufland/gazetka/5/",
        valid_from=datetime(2025, 2, 20, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2025, 3, 10, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.ACTIVE,
        page_count=14,
    )


@pytest.fixture
def leaflet_expired() -> Leaflet:
    """Expired leaflet (before 2025)."""
    return Leaflet(
        leaflet_id=6,
        shop_slug="biedronka",
        name="Old Promotion",
        cover_image_url="https://example.com/leaflet6.jpg",
        url="https://blix.pl/sklep/biedronka/gazetka/6/",
        valid_from=datetime(2024, 12, 1, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.ARCHIVED,
        page_count=8,
    )


@pytest.fixture
def leaflet_future() -> Leaflet:
    """Future leaflet (not yet valid)."""
    return Leaflet(
        leaflet_id=7,
        shop_slug="lidl",
        name="Future Campaign",
        cover_image_url="https://example.com/leaflet7.jpg",
        url="https://blix.pl/sklep/lidl/gazetka/7/",
        valid_from=datetime(2025, 4, 1, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2025, 4, 30, 23, 59, 59, tzinfo=timezone.utc),
        status=LeafletStatus.UPCOMING,
        page_count=12,
    )


@pytest.fixture
def all_test_leaflets(
    leaflet_january,
    leaflet_february,
    leaflet_march,
    leaflet_jan_feb,
    leaflet_feb_mar,
    leaflet_expired,
    leaflet_future,
) -> list[Leaflet]:
    """All test leaflets combined."""
    return [
        leaflet_january,
        leaflet_february,
        leaflet_march,
        leaflet_jan_feb,
        leaflet_feb_mar,
        leaflet_expired,
        leaflet_future,
    ]


# DateFilterOptions fixtures


@pytest.fixture
def filter_active_on_jan_15() -> DateFilterOptions:
    """Filter for leaflets active on January 15, 2025."""
    return DateFilterOptions(active_on=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc))


@pytest.fixture
def filter_active_on_feb_10() -> DateFilterOptions:
    """Filter for leaflets active on February 10, 2025."""
    return DateFilterOptions(active_on=datetime(2025, 2, 10, 12, 0, 0, tzinfo=timezone.utc))


@pytest.fixture
def filter_active_on_mar_15() -> DateFilterOptions:
    """Filter for leaflets active on March 15, 2025."""
    return DateFilterOptions(active_on=datetime(2025, 3, 15, 12, 0, 0, tzinfo=timezone.utc))


@pytest.fixture
def filter_date_from_feb_1() -> DateFilterOptions:
    """Filter for leaflets starting from February 1, 2025."""
    return DateFilterOptions(date_from=datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc))


@pytest.fixture
def filter_date_to_feb_28() -> DateFilterOptions:
    """Filter for leaflets ending by February 28, 2025."""
    return DateFilterOptions(date_to=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc))


@pytest.fixture
def filter_range_feb() -> DateFilterOptions:
    """Filter for leaflets in February 2025 (range filter)."""
    return DateFilterOptions(
        date_from=datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
        date_to=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc),
    )


@pytest.fixture
def filter_range_jan_to_mar() -> DateFilterOptions:
    """Filter for leaflets from January to March 2025."""
    return DateFilterOptions(
        date_from=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        date_to=datetime(2025, 3, 31, 23, 59, 59, tzinfo=timezone.utc),
    )


# =============================================================================
# Tests for load_all without filter
# =============================================================================


@pytest.mark.unit
class TestLoadAllWithoutFilter:
    """Tests for load_all method without date filter."""

    def test_returns_all_entities_when_no_filter_provided(self, leaflet_storage, all_test_leaflets):
        """Test load_all returns all entities when no filter provided."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.load_all()

        # Assert
        assert len(result) == 7
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert leaflet_ids == {1, 2, 3, 4, 5, 6, 7}

    def test_returns_all_entities_when_filter_is_none(self, leaflet_storage, all_test_leaflets):
        """Test load_all returns all entities when filter is None."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.load_all(date_filter=None)

        # Assert
        assert len(result) == 7

    def test_backward_compatibility(self, leaflet_storage, all_test_leaflets):
        """Test backward compatibility - load_all() works without argument."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - call without any argument (default behavior)
        result = leaflet_storage.load_all()

        # Assert
        assert len(result) == 7

    def test_returns_empty_list_when_no_entities(self, leaflet_storage):
        """Test load_all returns empty list when no entities stored."""
        # Act
        result = leaflet_storage.load_all()

        # Assert
        assert result == []

    def test_returns_empty_list_when_filter_provided_but_no_match(
        self, leaflet_storage, leaflet_january
    ):
        """Test load_all with filter returns empty list when no entities match."""
        # Arrange - only January leaflet stored
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act - filter for March (no match)
        filter_march = DateFilterOptions(
            active_on=datetime(2025, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_march)

        # Assert
        assert result == []


# =============================================================================
# Tests for load_all with active_on filter
# =============================================================================


@pytest.mark.unit
class TestLoadAllWithActiveOnFilter:
    """Tests for load_all method with active_on filter."""

    def test_filters_to_leaflets_active_on_specific_date(
        self, leaflet_storage, all_test_leaflets, filter_active_on_jan_15
    ):
        """Test filters to leaflets active on specific date."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.load_all(date_filter=filter_active_on_jan_15)

        # Assert
        # January 15, 2025 should match:
        # - leaflet_january (Jan 1-31)
        # - leaflet_jan_feb (Jan 15 - Feb 15)
        assert len(result) == 2
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert leaflet_ids == {1, 4}

    def test_returns_empty_list_when_no_leaflets_match(self, leaflet_storage, all_test_leaflets):
        """Test returns empty list when no leaflets match active_on filter."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - filter for a date with no active leaflets (May 2025)
        # Note: leaflet_future (Apr 1-30) is valid on Apr 15 but not May 15
        filter_may = DateFilterOptions(
            active_on=datetime(2025, 5, 15, 12, 0, 0, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_may)

        # Assert
        assert result == []

    def test_handles_timezone_correctly_with_aware_datetimes(
        self, leaflet_storage, leaflet_january
    ):
        """Test handles timezone-aware datetimes correctly."""
        # Arrange
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act - filter with timezone-aware datetime
        filter_utc = DateFilterOptions(
            active_on=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_utc)

        # Assert
        assert len(result) == 1
        assert result[0].leaflet_id == 1

    def test_handles_naive_datetime_as_utc(self, leaflet_storage, leaflet_january):
        """Test handles naive datetime by treating as UTC."""
        # Arrange
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act - filter with naive datetime (should be treated as UTC)
        filter_naive = DateFilterOptions(
            active_on=datetime(2025, 1, 15, 12, 0, 0)  # Naive datetime
        )
        result = leaflet_storage.load_all(date_filter=filter_naive)

        # Assert
        assert len(result) == 1

    def test_active_on_boundary_exact_start_date(self, leaflet_storage, leaflet_january):
        """Test active_on with exact start date boundary."""
        # Arrange
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act - filter for exact valid_from date
        filter_exact = DateFilterOptions(
            active_on=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_exact)

        # Assert - should include leaflet valid from Jan 1
        assert len(result) == 1
        assert result[0].leaflet_id == 1

    def test_active_on_boundary_exact_end_date(self, leaflet_storage, leaflet_january):
        """Test active_on with exact end date boundary."""
        # Arrange
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act - filter for exact valid_until date
        filter_exact = DateFilterOptions(
            active_on=datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_exact)

        # Assert - should include leaflet valid until Jan 31
        assert len(result) == 1
        assert result[0].leaflet_id == 1


# =============================================================================
# Tests for load_all with date_from filter
# =============================================================================


@pytest.mark.unit
class TestLoadAllWithDateFromFilter:
    """Tests for load_all method with date_from (valid_from) filter."""

    def test_filters_leaflets_starting_from_specific_date(
        self, leaflet_storage, all_test_leaflets, filter_date_from_feb_1
    ):
        """Test filters leaflets starting from specific date."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.load_all(date_filter=filter_date_from_feb_1)

        # Assert
        # date_from filter: entity.valid_from >= date_from
        # Starting from Feb 1, 2025 should include (valid_from >= Feb 1):
        # - leaflet_february (Feb 1-28) - valid_from=Feb 1 ✓
        # - leaflet_feb_mar (Feb 20 - Mar 10) - valid_from=Feb 20 ✓
        # - leaflet_march (Mar 1-31) - valid_from=Mar 1 ✓
        # - leaflet_future (Apr 1-30) - valid_from=Apr 1 ✓
        # Excludes (valid_from < Feb 1):
        # - leaflet_january (Jan 1-31) - valid_from=Jan 1 ✗
        # - leaflet_jan_feb (Jan 15 - Feb 15) - valid_from=Jan 15 ✗
        # - leaflet_expired (Dec 2024) - valid_from=Dec 1 ✗
        assert len(result) == 4
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert leaflet_ids == {2, 3, 5, 7}

    def test_date_from_boundary_exact_date_match(self, leaflet_storage, leaflet_february):
        """Test boundary condition - exact date match with date_from."""
        # Arrange
        leaflet_storage.save(leaflet_february, "leaflet_2.json")

        # Act - filter starting exactly on valid_from date
        filter_exact = DateFilterOptions(
            date_from=datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_exact)

        # Assert
        assert len(result) == 1
        assert result[0].leaflet_id == 2

    def test_date_from_excludes_leaflets_starting_before_filter(
        self, leaflet_storage, all_test_leaflets
    ):
        """Test date_from excludes leaflets starting before the filter date."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - filter starting from March 1
        filter_march = DateFilterOptions(
            date_from=datetime(2025, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_march)

        # Assert - should exclude January and February leaflets
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert 1 not in leaflet_ids  # January
        assert 2 not in leaflet_ids  # February
        assert 3 in leaflet_ids  # March
        assert 7 in leaflet_ids  # Future

    def test_valid_from_alias_works(self, leaflet_storage, leaflet_february):
        """Test that valid_from alias works same as date_from."""
        # Arrange
        leaflet_storage.save(leaflet_february, "leaflet_2.json")

        # Act - use valid_from instead of date_from
        filter_valid_from = DateFilterOptions(
            valid_from=datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_valid_from)

        # Assert
        assert len(result) == 1
        assert result[0].leaflet_id == 2


# =============================================================================
# Tests for load_all with date_to filter
# =============================================================================


@pytest.mark.unit
class TestLoadAllWithDateToFilter:
    """Tests for load_all method with date_to (valid_until) filter."""

    def test_filters_leaflets_ending_by_specific_date(
        self, leaflet_storage, all_test_leaflets, filter_date_to_feb_28
    ):
        """Test filters leaflets ending by specific date."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.load_all(date_filter=filter_date_to_feb_28)

        # Assert
        # date_to filter: entity.valid_until <= date_to
        # Ending by Feb 28, 2025 should include (valid_until <= Feb 28):
        # - leaflet_january (Jan 1-31) - valid_until=Jan 31 ✓
        # - leaflet_february (Feb 1-28) - valid_until=Feb 28 ✓
        # - leaflet_jan_feb (Jan 15 - Feb 15) - valid_until=Feb 15 ✓
        # - leaflet_expired (Dec 2024) - valid_until=Dec 31 2024 ✓
        # Excludes (valid_until > Feb 28):
        # - leaflet_feb_mar (Feb 20 - Mar 10) - valid_until=Mar 10 ✗
        # - leaflet_march (Mar 1-31) - valid_until=Mar 31 ✗
        # - leaflet_future (Apr 1-30) - valid_until=Apr 30 ✗
        assert len(result) == 4
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert leaflet_ids == {1, 2, 4, 6}

    def test_date_to_boundary_exact_date_match(self, leaflet_storage, leaflet_february):
        """Test boundary condition - exact date match with date_to."""
        # Arrange
        leaflet_storage.save(leaflet_february, "leaflet_2.json")

        # Act - filter ending exactly on valid_until date
        filter_exact = DateFilterOptions(
            date_to=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_exact)

        # Assert
        assert len(result) == 1
        assert result[0].leaflet_id == 2

    def test_date_to_excludes_leaflets_ending_after_filter(
        self, leaflet_storage, all_test_leaflets
    ):
        """Test date_to excludes leaflets ending after the filter date."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - filter ending by January 31
        filter_jan = DateFilterOptions(
            date_to=datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_jan)

        # Assert - should include January leaflets and expired ones
        # date_to filter: entity.valid_until <= date_to
        # - leaflet_january (Jan 1-31) - valid_until=Jan 31 ✓
        # - leaflet_expired (Dec 2024) - valid_until=Dec 31 2024 ✓
        # Excludes:
        # - leaflet_jan_feb (Jan 15 - Feb 15) - valid_until=Feb 15 > Jan 31 ✗
        # - leaflet_february (Feb 1-28) - valid_until=Feb 28 > Jan 31 ✗
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert leaflet_ids == {1, 6}

    def test_valid_until_alias_works(self, leaflet_storage, leaflet_february):
        """Test that valid_until alias works same as date_to."""
        # Arrange
        leaflet_storage.save(leaflet_february, "leaflet_2.json")

        # Act - use valid_until instead of date_to
        filter_valid_until = DateFilterOptions(
            valid_until=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc)
        )
        result = leaflet_storage.load_all(date_filter=filter_valid_until)

        # Assert
        assert len(result) == 1
        assert result[0].leaflet_id == 2


# =============================================================================
# Tests for load_all with range filter (date_from + date_to)
# =============================================================================


@pytest.mark.unit
class TestLoadAllWithRangeFilter:
    """Tests for load_all method with date range filter (date_from + date_to)."""

    def test_filters_leaflets_within_date_range(
        self, leaflet_storage, all_test_leaflets, filter_range_feb
    ):
        """Test filters leaflets within date range."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.load_all(date_filter=filter_range_feb)

        # Assert
        # Range filter: entity.valid_from >= date_from AND entity.valid_until <= date_to
        # Within Feb 1-28, 2025:
        # - leaflet_february (Feb 1-28): valid_from=Feb 1 >= Feb 1 ✓ AND valid_until=Feb 28 <= Feb 28 ✓
        # - leaflet_jan_feb (Jan 15 - Feb 15): valid_from=Jan 15 >= Feb 1 ✗ → excluded
        # - leaflet_feb_mar (Feb 20 - Mar 10): valid_until=Mar 10 <= Feb 28 ✗ → excluded
        # Excludes: leaflet_january (valid_from < Feb 1), leaflet_march, leaflet_future, leaflet_expired
        assert len(result) == 1
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert leaflet_ids == {2}

    def test_overlapping_ranges(self, leaflet_storage, all_test_leaflets):
        """Test with overlapping date ranges."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - filter for January to March range
        result = leaflet_storage.load_all(
            date_filter=DateFilterOptions(
                date_from=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                date_to=datetime(2025, 3, 31, 23, 59, 59, tzinfo=timezone.utc),
            )
        )

        # Assert - containment filter: valid_from >= Jan 1 AND valid_until <= Mar 31
        # - leaflet_january (Jan 1-31): valid_from=Jan 1 >= Jan 1 ✓ AND valid_until=Jan 31 <= Mar 31 ✓
        # - leaflet_february (Feb 1-28): valid_from=Feb 1 >= Jan 1 ✓ AND valid_until=Feb 28 <= Mar 31 ✓
        # - leaflet_march (Mar 1-31): valid_from=Mar 1 >= Jan 1 ✓ AND valid_until=Mar 31 <= Mar 31 ✓
        # - leaflet_jan_feb (Jan 15 - Feb 15): valid_from=Jan 15 >= Jan 1 ✓ AND valid_until=Feb 15 <= Mar 31 ✓
        # - leaflet_feb_mar (Feb 20 - Mar 10): valid_from=Feb 20 >= Jan 1 ✓ AND valid_until=Mar 10 <= Mar 31 ✓
        # Excludes:
        # - leaflet_expired: valid_from=Dec 1 >= Jan 1 ✗
        # - leaflet_future: valid_until=Apr 30 <= Mar 31 ✗
        assert len(result) == 5
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert leaflet_ids == {1, 2, 3, 4, 5}

    def test_partial_overlaps(self, leaflet_storage, all_test_leaflets):
        """Test filters leaflets with partial date overlap."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - narrow range that only overlaps with some
        filter_partial = DateFilterOptions(
            date_from=datetime(2025, 2, 10, 0, 0, 0, tzinfo=timezone.utc),
            date_to=datetime(2025, 2, 20, 23, 59, 59, tzinfo=timezone.utc),
        )
        result = leaflet_storage.load_all(date_filter=filter_partial)

        # Assert - containment filter: valid_from >= Feb 10 AND valid_until <= Feb 20
        # - leaflet_february (Feb 1-28): valid_from=Feb 1 >= Feb 10 ✗ → excluded
        # - leaflet_jan_feb (Jan 15 - Feb 15): valid_from=Jan 15 >= Feb 10 ✗ → excluded
        # - leaflet_feb_mar (Feb 20 - Mar 10): valid_until=Mar 10 <= Feb 20 ✗ → excluded
        # All leaflets fail containment check, so empty result
        assert len(result) == 0
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        assert leaflet_ids == set()

    def test_range_with_no_matches(self, leaflet_storage, all_test_leaflets):
        """Test range filter returns empty when no leaflets match."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - range outside all leaflet dates
        filter_no_match = DateFilterOptions(
            date_from=datetime(2025, 5, 1, 0, 0, 0, tzinfo=timezone.utc),
            date_to=datetime(2025, 5, 31, 23, 59, 59, tzinfo=timezone.utc),
        )
        result = leaflet_storage.load_all(date_filter=filter_no_match)

        # Assert
        assert result == []

    def test_range_boundary_exact_match(self, leaflet_storage, leaflet_jan_feb):
        """Test range with exact boundary matches."""
        # Arrange
        leaflet_storage.save(leaflet_jan_feb, "leaflet_4.json")

        # Act - exact match on both boundaries
        filter_exact = DateFilterOptions(
            date_from=datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
            date_to=datetime(2025, 2, 15, 23, 59, 59, tzinfo=timezone.utc),
        )
        result = leaflet_storage.load_all(date_filter=filter_exact)

        # Assert
        assert len(result) == 1
        assert result[0].leaflet_id == 4


# =============================================================================
# Tests for count method
# =============================================================================


@pytest.mark.unit
class TestCountMethod:
    """Tests for count method."""

    def test_count_without_filter(self, leaflet_storage, all_test_leaflets):
        """Test count returns total without filter."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        count = leaflet_storage.count()

        # Assert
        assert count == 7

    def test_count_with_filter(self, leaflet_storage, all_test_leaflets, filter_active_on_jan_15):
        """Test count with date filter."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        count = leaflet_storage.count(date_filter=filter_active_on_jan_15)

        # Assert
        assert count == 2  # leaflet_january and leaflet_jan_feb

    def test_count_returns_0_when_no_matches(self, leaflet_storage, all_test_leaflets):
        """Test count returns 0 when no entities match filter."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - filter for future date with no leaflets
        filter_future = DateFilterOptions(
            active_on=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        )
        count = leaflet_storage.count(date_filter=filter_future)

        # Assert
        assert count == 0

    def test_count_returns_0_when_empty_storage(self, leaflet_storage):
        """Test count returns 0 when no entities stored."""
        # Act
        count = leaflet_storage.count()

        # Assert
        assert count == 0

    def test_count_with_range_filter(self, leaflet_storage, all_test_leaflets):
        """Test count with range filter."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        count = leaflet_storage.count(
            date_filter=DateFilterOptions(
                date_from=datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
                date_to=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc),
            )
        )

        # Assert - containment: valid_from >= Feb 1 AND valid_until <= Feb 28
        # Only leaflet_february (Feb 1-28) satisfies both conditions
        assert count == 1


# =============================================================================
# Tests for exists method
# =============================================================================


@pytest.mark.unit
class TestExistsMethod:
    """Tests for exists method."""

    def test_exists_returns_true_when_entities_present(self, leaflet_storage, leaflet_january):
        """Test exists returns True when entities present."""
        # Arrange
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act
        result = leaflet_storage.exists()

        # Assert
        assert result is True

    def test_exists_returns_false_when_no_entities(self, leaflet_storage):
        """Test exists returns False when no entities."""
        # Act
        result = leaflet_storage.exists()

        # Assert
        assert result is False

    def test_exists_with_filter_returns_true_when_match(self, leaflet_storage, all_test_leaflets):
        """Test exists with filter returns True when entities match."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.exists(
            date_filter=DateFilterOptions(
                active_on=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            )
        )

        # Assert
        assert result is True

    def test_exists_with_filter_returns_false_when_no_match(
        self, leaflet_storage, all_test_leaflets
    ):
        """Test exists with filter returns False when no entities match."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.exists(
            date_filter=DateFilterOptions(
                active_on=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
            )
        )

        # Assert
        assert result is False

    def test_exists_with_range_filter(self, leaflet_storage, all_test_leaflets):
        """Test exists with range filter."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act - range with matches
        result_match = leaflet_storage.exists(
            date_filter=DateFilterOptions(
                date_from=datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
                date_to=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc),
            )
        )

        # Act - range without matches
        result_no_match = leaflet_storage.exists(
            date_filter=DateFilterOptions(
                date_from=datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
                date_to=datetime(2025, 6, 30, 23, 59, 59, tzinfo=timezone.utc),
            )
        )

        # Assert
        assert result_match is True
        assert result_no_match is False


# =============================================================================
# Tests for logging
# =============================================================================


@pytest.mark.unit
class TestLogging:
    """Tests for logging functionality."""

    def test_logging_called_during_filtering(self, leaflet_storage, all_test_leaflets):
        """Verify logging calls are made during filtering."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        with patch("src.storage.date_filtered_storage.logger") as mock_logger:
            filter_options = DateFilterOptions(
                active_on=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            )
            leaflet_storage.load_all(date_filter=filter_options)

            # Assert - verify logging was called
            mock_logger.info.assert_called_once()

    def test_log_context_includes_filter_parameters(self, leaflet_storage, all_test_leaflets):
        """Check log context includes filter parameters."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        with patch("src.storage.date_filtered_storage.logger") as mock_logger:
            filter_options = DateFilterOptions(
                active_on=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            )
            leaflet_storage.load_all(date_filter=filter_options)

            # Assert - verify log context
            call_args = mock_logger.info.call_args
            log_kwargs = call_args.kwargs

            assert "total_entities" in log_kwargs
            assert "filtered_entities" in log_kwargs
            assert log_kwargs["total_entities"] == 7
            assert log_kwargs["filtered_entities"] == 2
            assert log_kwargs["filter_active_on"] is not None

    def test_log_context_includes_date_from(self, leaflet_storage, all_test_leaflets):
        """Check log context includes date_from parameter."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        with patch("src.storage.date_filtered_storage.logger") as mock_logger:
            filter_options = DateFilterOptions(
                date_from=datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
            )
            leaflet_storage.load_all(date_filter=filter_options)

            # Assert
            call_args = mock_logger.info.call_args
            log_kwargs = call_args.kwargs

            assert log_kwargs["filter_date_from"] is not None

    def test_log_context_includes_date_to(self, leaflet_storage, all_test_leaflets):
        """Check log context includes date_to parameter."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        with patch("src.storage.date_filtered_storage.logger") as mock_logger:
            filter_options = DateFilterOptions(
                date_to=datetime(2025, 2, 28, 23, 59, 59, tzinfo=timezone.utc)
            )
            leaflet_storage.load_all(date_filter=filter_options)

            # Assert
            call_args = mock_logger.info.call_args
            log_kwargs = call_args.kwargs

            assert log_kwargs["filter_date_to"] is not None

    def test_no_logging_without_filter(self, leaflet_storage, all_test_leaflets):
        """Verify no logging when no filter provided."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        with patch("src.storage.date_filtered_storage.logger") as mock_logger:
            leaflet_storage.load_all()

            # Assert - info should not be called when no filter
            mock_logger.info.assert_not_called()

    def test_no_logging_when_filter_has_no_criteria(self, leaflet_storage, leaflet_january):
        """Verify no logging when filter has no date criteria."""
        # Arrange
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act - filter object created but no actual date criteria
        with patch("src.storage.date_filtered_storage.logger") as mock_logger:
            empty_filter = DateFilterOptions()  # No filter criteria set
            leaflet_storage.load_all(date_filter=empty_filter)

            # Assert - info should not be called when filter has no criteria
            mock_logger.info.assert_not_called()


# =============================================================================
# Additional edge case tests
# =============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_leaflet_filtered(self, leaflet_storage, leaflet_january):
        """Test with single leaflet that matches filter."""
        # Arrange
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act
        result = leaflet_storage.load_all(
            date_filter=DateFilterOptions(
                active_on=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            )
        )

        # Assert
        assert len(result) == 1
        assert result[0].leaflet_id == 1

    def test_single_leaflet_not_matched(self, leaflet_storage, leaflet_january):
        """Test with single leaflet that doesn't match filter."""
        # Arrange
        leaflet_storage.save(leaflet_january, "leaflet_1.json")

        # Act
        result = leaflet_storage.load_all(
            date_filter=DateFilterOptions(
                active_on=datetime(2025, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
            )
        )

        # Assert
        assert len(result) == 0

    def test_expired_leaflet_excluded(self, leaflet_storage, leaflet_expired):
        """Test expired leaflet is properly excluded."""
        # Arrange
        leaflet_storage.save(leaflet_expired, "leaflet_6.json")

        # Act - filter for current date
        result = leaflet_storage.load_all(
            date_filter=DateFilterOptions(
                active_on=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            )
        )

        # Assert
        assert len(result) == 0

    def test_future_leaflet_excluded(self, leaflet_storage, leaflet_future):
        """Test future leaflet is properly excluded."""
        # Arrange
        leaflet_storage.save(leaflet_future, "leaflet_7.json")

        # Act - filter for current date
        result = leaflet_storage.load_all(
            date_filter=DateFilterOptions(
                active_on=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            )
        )

        # Assert
        assert len(result) == 0

    def test_filter_with_only_date_from_returns_all_starting_after(
        self, leaflet_storage, all_test_leaflets
    ):
        """Test filter with only date_from returns all starting after that date."""
        # Arrange
        for leaflet in all_test_leaflets:
            leaflet_storage.save(leaflet, f"leaflet_{leaflet.leaflet_id}.json")

        # Act
        result = leaflet_storage.load_all(
            date_filter=DateFilterOptions(
                date_from=datetime(2025, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
            )
        )

        # Assert
        # date_from: entity.valid_from >= date_from
        leaflet_ids = {leaflet.leaflet_id for leaflet in result}
        # Should include: march (valid_from=Mar 1 >= Mar 1), future (valid_from=Apr 1 >= Mar 1)
        assert 3 in leaflet_ids  # March - valid_from=Mar 1 >= Mar 1 ✓
        assert 7 in leaflet_ids  # Future - valid_from=Apr 1 >= Mar 1 ✓
        # Should exclude: feb_mar (valid_from=Feb 20 < Mar 1), january, february, jan_feb, expired
        assert 5 not in leaflet_ids  # Feb-Mar - valid_from=Feb 20 < Mar 1 ✗
        assert 1 not in leaflet_ids
        assert 2 not in leaflet_ids
        assert 4 not in leaflet_ids
        assert 6 not in leaflet_ids
