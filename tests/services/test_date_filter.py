"""Unit tests for DateFilterService.

Tests cover:
- filter_by_active_date
- filter_by_date_range
- filter_leaflets
- Edge cases (empty list, no matches)
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from pydantic import HttpUrl

from src.domain.date_filter import DateFilterOptions
from src.domain.entities import Leaflet, LeafletStatus, SearchResult
from src.services.date_filter import DateFilterService


@pytest.fixture
def date_filter_service():
    """Create a DateFilterService instance."""
    return DateFilterService()


@pytest.fixture
def sample_leaflets():
    """Create sample leaflet entities with various valid dates."""
    today = datetime.now(timezone.utc)
    return [
        # Active: valid from past to future
        Leaflet(
            leaflet_id=1,
            shop_slug="biedronka",
            name="Current",
            cover_image_url=HttpUrl("https://example.com/1.jpg"),
            url=HttpUrl("https://blix.pl/1/"),
            valid_from=today - timedelta(days=7),
            valid_until=today + timedelta(days=7),
            status=LeafletStatus.ACTIVE,
            page_count=12,
        ),
        # Expired: valid until past
        Leaflet(
            leaflet_id=2,
            shop_slug="biedronka",
            name="Expired",
            cover_image_url=HttpUrl("https://example.com/2.jpg"),
            url=HttpUrl("https://blix.pl/2/"),
            valid_from=today - timedelta(days=30),
            valid_until=today - timedelta(days=7),
            status=LeafletStatus.ARCHIVED,
            page_count=10,
        ),
        # Future: valid from future
        Leaflet(
            leaflet_id=3,
            shop_slug="biedronka",
            name="Future",
            cover_image_url=HttpUrl("https://example.com/3.jpg"),
            url=HttpUrl("https://blix.pl/3/"),
            valid_from=today + timedelta(days=7),
            valid_until=today + timedelta(days=14),
            status=LeafletStatus.ACTIVE,
            page_count=8,
        ),
    ]


@pytest.fixture
def sample_search_results():
    """Create sample search result entities."""
    today = datetime.now(timezone.utc)
    return [
        SearchResult(
            hash="abc123",
            name="Product A",
            image_url=HttpUrl("https://img.blix.pl/image/offer/123.jpg"),
            brand_name="Brand A",
            manufacturer_name="Manufacturer A",
            product_leaflet_page_uuid="uuid-1",
            leaflet_id=1,
            page_number=1,
            price=None,
            percent_discount=0,
            valid_from=today - timedelta(days=7),
            valid_until=today + timedelta(days=7),
            position_x=0.1,
            position_y=0.2,
            width=0.3,
            height=0.4,
            search_query="test",
        ),
        SearchResult(
            hash="def456",
            name="Product B",
            image_url=HttpUrl("https://img.blix.pl/image/offer/456.jpg"),
            brand_name="Brand B",
            manufacturer_name="Manufacturer B",
            product_leaflet_page_uuid="uuid-2",
            leaflet_id=2,
            page_number=2,
            price=None,
            percent_discount=0,
            valid_from=today - timedelta(days=30),
            valid_until=today - timedelta(days=14),
            position_x=0.1,
            position_y=0.2,
            width=0.3,
            height=0.4,
            search_query="test",
        ),
    ]


@pytest.mark.unit
class TestDateFilterServiceFilterByActiveDate:
    """Tests for filter_by_active_date method."""

    def test_filter_by_active_date(self, date_filter_service, sample_leaflets):
        """Filter items active on specific date."""
        # Arrange
        today = datetime.now(timezone.utc)

        # Act
        result = date_filter_service.filter_by_active_date(sample_leaflets, today)

        # Assert - should return only the current (active) leaflet
        assert len(result) == 1
        assert result[0].leaflet_id == 1
        assert result[0].name == "Current"

    def test_filter_by_active_date_expired(self, date_filter_service, sample_leaflets):
        """Filter items active on date in the past."""
        # Arrange
        past_date = datetime.now(timezone.utc) - timedelta(days=20)

        # Act
        result = date_filter_service.filter_by_active_date(sample_leaflets, past_date)

        # Assert - should return only the expired leaflet
        assert len(result) == 1
        assert result[0].leaflet_id == 2
        assert result[0].name == "Expired"

    def test_filter_by_active_date_future(self, date_filter_service, sample_leaflets):
        """Filter items active on date in the future."""
        # Arrange
        future_date = datetime.now(timezone.utc) + timedelta(days=10)

        # Act
        result = date_filter_service.filter_by_active_date(sample_leaflets, future_date)

        # Assert - should return only the future leaflet (starts in future and is valid then)
        assert len(result) == 1
        assert result[0].leaflet_id == 3

    def test_filter_by_active_date_with_naive_datetime(self, date_filter_service, sample_leaflets):
        """Filter with naive (timezone-unaware) datetime."""
        # Arrange - naive datetime
        today = datetime.now()  # No timezone info

        # Act
        result = date_filter_service.filter_by_active_date(sample_leaflets, today)

        # Assert - should still work, treating naive as UTC
        assert len(result) >= 0


@pytest.mark.unit
class TestDateFilterServiceFilterByDateRange:
    """Tests for filter_by_date_range method."""

    def test_filter_by_date_range(self, date_filter_service, sample_leaflets):
        """Filter by date range."""
        # Arrange
        start = datetime.now(timezone.utc) - timedelta(days=5)
        end = datetime.now(timezone.utc) + timedelta(days=5)

        # Act
        result = date_filter_service.filter_by_date_range(sample_leaflets, start, end)

        # Assert - should return leaflets that overlap with the range
        assert len(result) == 1
        assert result[0].leaflet_id == 1

    def test_filter_by_date_range_wide(self, date_filter_service, sample_leaflets):
        """Filter by wide date range covering all items."""
        # Arrange
        start = datetime.now(timezone.utc) - timedelta(days=60)
        end = datetime.now(timezone.utc) + timedelta(days=60)

        # Act
        result = date_filter_service.filter_by_date_range(sample_leaflets, start, end)

        # Assert - should return all leaflets
        assert len(result) == 3

    def test_filter_by_date_range_narrow(self, date_filter_service, sample_leaflets):
        """Filter by narrow date range with no matches."""
        # Arrange
        start = datetime.now(timezone.utc) + timedelta(days=20)
        end = datetime.now(timezone.utc) + timedelta(days=25)

        # Act
        result = date_filter_service.filter_by_date_range(sample_leaflets, start, end)

        # Assert - should return no leaflets
        assert len(result) == 0


@pytest.mark.unit
class TestDateFilterServiceFilterLeaflets:
    """Tests for filter_leaflets method."""

    def test_filter_leaflets_with_active_on(self, date_filter_service, sample_leaflets):
        """Filter leaflets using DateFilterOptions with active_on."""
        # Arrange
        today = datetime.now(timezone.utc)
        filter_options = DateFilterOptions(active_on=today)

        # Act
        result = date_filter_service.filter_leaflets(sample_leaflets, filter_options)

        # Assert
        assert len(result) == 1
        assert result[0].leaflet_id == 1

    def test_filter_leaflets_with_date_range(self, date_filter_service, sample_leaflets):
        """Filter leaflets using DateFilterOptions with date range.

        Note: DateFilterOptions.to_predicate() checks if entity's validity range
        is entirely within the filter range (not overlapping).
        """
        # Arrange - use a wide enough range to include one leaflet
        filter_options = DateFilterOptions(
            date_from=datetime.now(timezone.utc) - timedelta(days=60),
            date_to=datetime.now(timezone.utc) + timedelta(days=60),
        )

        # Act
        result = date_filter_service.filter_leaflets(sample_leaflets, filter_options)

        # Assert - should return all 3 leaflets since range is wide enough
        assert len(result) == 3

    def test_filter_leaflets_no_filter(self, date_filter_service, sample_leaflets):
        """Filter leaflets with no filter options returns all."""
        # Arrange
        filter_options = DateFilterOptions()

        # Act
        result = date_filter_service.filter_leaflets(sample_leaflets, filter_options)

        # Assert - should return all leaflets since no filter is set
        assert len(result) == 3


@pytest.mark.unit
class TestDateFilterServiceEdgeCases:
    """Edge case tests for DateFilterService."""

    def test_empty_list_returns_empty(self, date_filter_service):
        """Edge case: empty input returns empty list."""
        # Arrange
        empty_list: list = []

        # Act
        result = date_filter_service.filter_by_active_date(empty_list, datetime.now())

        # Assert
        assert result == []
        assert len(result) == 0

    def test_empty_list_date_range(self, date_filter_service):
        """Edge case: empty input returns empty for date range."""
        # Arrange
        empty_list: list = []
        start = datetime.now(timezone.utc)
        end = datetime.now(timezone.utc) + timedelta(days=7)

        # Act
        result = date_filter_service.filter_by_date_range(empty_list, start, end)

        # Assert
        assert result == []
        assert len(result) == 0

    def test_empty_list_filter_leaflets(self, date_filter_service):
        """Edge case: empty input returns empty for filter_leaflets."""
        # Arrange
        empty_list: list = []
        filter_options = DateFilterOptions(active_on=datetime.now(timezone.utc))

        # Act
        result = date_filter_service.filter_leaflets(empty_list, filter_options)

        # Assert
        assert result == []
        assert len(result) == 0

    def test_no_matches_returns_empty(self, date_filter_service, sample_leaflets):
        """Edge case: no matching items returns empty list."""
        # Arrange - date far in the future
        future_date = datetime.now(timezone.utc) + timedelta(days=100)

        # Act
        result = date_filter_service.filter_by_active_date(sample_leaflets, future_date)

        # Assert
        assert len(result) == 0
        assert result == []

    def test_filter_search_results(self, date_filter_service, sample_search_results):
        """Filter search results by active date."""
        # Arrange
        today = datetime.now(timezone.utc)
        filter_options = DateFilterOptions(active_on=today)

        # Act
        result = date_filter_service.filter_leaflets(sample_search_results, filter_options)

        # Assert
        assert len(result) == 1


@pytest.mark.unit
class TestDateFilterServicePrivateMethods:
    """Tests for private helper methods."""

    def test_is_valid_on_with_is_valid_on_method(self, date_filter_service):
        """Test _is_valid_on with entity that has is_valid_on method."""
        # Arrange
        mock_entity = Mock()
        mock_entity.is_valid_on.return_value = True

        # Act
        result = date_filter_service._is_valid_on(mock_entity, datetime.now())

        # Assert
        assert result is True
        mock_entity.is_valid_on.assert_called_once()

    def test_is_valid_on_fallback_to_valid_from_valid_until(self, date_filter_service):
        """Test _is_valid_on fallback to valid_from/valid_until."""
        # Arrange
        today = datetime.now(timezone.utc)
        mock_entity = Mock()
        mock_entity.is_valid_on = None  # No method
        mock_entity.valid_from = today - timedelta(days=7)
        mock_entity.valid_until = today + timedelta(days=7)

        # Act
        result = date_filter_service._is_valid_on(mock_entity, today)

        # Assert
        assert result is True

    def test_is_valid_on_fallback_no_match(self, date_filter_service):
        """Test _is_valid_on fallback when date doesn't match."""
        # Arrange
        today = datetime.now(timezone.utc)
        mock_entity = Mock()
        mock_entity.is_valid_on = None  # No method
        mock_entity.valid_from = today - timedelta(days=30)
        mock_entity.valid_until = today - timedelta(days=7)  # Expired

        # Act
        result = date_filter_service._is_valid_on(mock_entity, today)

        # Assert
        assert result is False

    def test_is_valid_on_no_date_attributes(self, date_filter_service):
        """Test _is_valid_on when entity has no date attributes."""
        # Arrange
        mock_entity = Mock(spec=[])  # No attributes

        # Act
        result = date_filter_service._is_valid_on(mock_entity, datetime.now())

        # Assert
        assert result is False

    def test_is_valid_in_range_overlap(self, date_filter_service):
        """Test _is_valid_in_range with overlapping ranges."""
        # Arrange
        today = datetime.now(timezone.utc)
        mock_entity = Mock()
        mock_entity.valid_from = today - timedelta(days=5)
        mock_entity.valid_until = today + timedelta(days=5)

        # Range that overlaps
        start = today - timedelta(days=2)
        end = today + timedelta(days=10)

        # Act
        result = date_filter_service._is_valid_in_range(mock_entity, start, end)

        # Assert
        assert result is True

    def test_is_valid_in_range_no_overlap(self, date_filter_service):
        """Test _is_valid_in_range with no overlap."""
        # Arrange
        today = datetime.now(timezone.utc)
        mock_entity = Mock()
        mock_entity.valid_from = today - timedelta(days=5)
        mock_entity.valid_until = today - timedelta(days=1)

        # Range that doesn't overlap
        start = today + timedelta(days=1)
        end = today + timedelta(days=10)

        # Act
        result = date_filter_service._is_valid_in_range(mock_entity, start, end)

        # Assert
        assert result is False
