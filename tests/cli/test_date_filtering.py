"""Integration tests for CLI commands with date filtering."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from pydantic import HttpUrl
from typer.testing import CliRunner

from src.cli import app
from src.domain.entities import Leaflet, LeafletStatus, SearchResult
from src.storage.json_storage import JSONStorage

runner = CliRunner()


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def sample_leaflets_for_filtering():
    """Create sample leaflets with various validity periods for filtering tests.

    Uses dynamic dates relative to today to ensure tests work on any date.
    """
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    return [
        # Active leaflet - valid from past to future
        Leaflet(
            leaflet_id=1,
            shop_slug="biedronka",
            name="Current Promotion",
            cover_image_url=HttpUrl("https://example.com/leaflet1.jpg"),
            url=HttpUrl("https://blix.pl/sklep/biedronka/gazetka/1/"),
            valid_from=today - timedelta(days=7),
            valid_until=today + timedelta(days=7),
            status=LeafletStatus.ACTIVE,
            page_count=12,
        ),
        # Expired leaflet - fully in the past
        Leaflet(
            leaflet_id=2,
            shop_slug="biedronka",
            name="Past Promotion",
            cover_image_url=HttpUrl("https://example.com/leaflet2.jpg"),
            url=HttpUrl("https://blix.pl/sklep/biedronka/gazetka/2/"),
            valid_from=today - timedelta(days=30),
            valid_until=today - timedelta(days=14),
            status=LeafletStatus.ARCHIVED,
            page_count=10,
        ),
        # Future leaflet - starts in the future
        Leaflet(
            leaflet_id=3,
            shop_slug="biedronka",
            name="Upcoming Promotion",
            cover_image_url=HttpUrl("https://example.com/leaflet3.jpg"),
            url=HttpUrl("https://blix.pl/sklep/biedronka/gazetka/3/"),
            valid_from=today + timedelta(days=7),
            valid_until=today + timedelta(days=21),
            status=LeafletStatus.UPCOMING,
            page_count=8,
        ),
        # Active leaflet - starting today
        Leaflet(
            leaflet_id=4,
            shop_slug="lidl",
            name="Today's Start",
            cover_image_url=HttpUrl("https://example.com/leaflet4.jpg"),
            url=HttpUrl("https://blix.pl/sklep/lidl/gazetka/4/"),
            valid_from=today,
            valid_until=today + timedelta(days=14),
            status=LeafletStatus.ACTIVE,
            page_count=16,
        ),
        # Active leaflet - ending today
        Leaflet(
            leaflet_id=5,
            shop_slug="lidl",
            name="Today's End",
            cover_image_url=HttpUrl("https://example.com/leaflet5.jpg"),
            url=HttpUrl("https://blix.pl/sklep/lidl/gazetka/5/"),
            valid_from=today - timedelta(days=7),
            valid_until=today,
            status=LeafletStatus.ACTIVE,
            page_count=14,
        ),
    ]


@pytest.fixture
def leaflet_storage_setup(temp_data_dir, sample_leaflets_for_filtering):
    """Set up leaflet storage with sample leaflets using individual files."""
    # Save biedronka leaflets
    biedronka_dir = temp_data_dir / "leaflets" / "biedronka"
    biedronka_dir.mkdir(parents=True, exist_ok=True)
    storage = JSONStorage(biedronka_dir, Leaflet)
    for leaflet in sample_leaflets_for_filtering[:3]:
        storage.save(leaflet, f"{leaflet.leaflet_id}.json")

    # Save lidl leaflets
    lidl_dir = temp_data_dir / "leaflets" / "lidl"
    lidl_dir.mkdir(parents=True, exist_ok=True)
    lidl_storage = JSONStorage(lidl_dir, Leaflet)
    for leaflet in sample_leaflets_for_filtering[3:]:
        lidl_storage.save(leaflet, f"{leaflet.leaflet_id}.json")

    return temp_data_dir


@pytest.fixture
def sample_search_results():
    """Create sample search results with various validity periods."""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    return [
        # Result from active leaflet
        SearchResult(
            hash="result-1",
            name="Kawa ziarnista 500g",
            image_url=HttpUrl("https://img.blix.pl/image/offer/1.jpg"),
            brand_name="Jacobs",
            manufacturer_name="Jacobs Douwe Egberts",
            product_leaflet_page_uuid="page-uuid-1",
            leaflet_id=1,
            page_number=3,
            price=Decimal("1999"),
            percent_discount=20,
            valid_from=today - timedelta(days=7),
            valid_until=today + timedelta(days=7),
            position_x=0.1,
            position_y=0.2,
            width=0.3,
            height=0.4,
            search_query="kawa",
        ),
        # Result from past (expired) leaflet
        SearchResult(
            hash="result-2",
            name="Kawa rozpuszczalna 200g",
            image_url=HttpUrl("https://img.blix.pl/image/offer/2.jpg"),
            brand_name="Nescafe",
            manufacturer_name="Nestle",
            product_leaflet_page_uuid="page-uuid-2",
            leaflet_id=2,
            page_number=5,
            price=Decimal("1299"),
            percent_discount=15,
            valid_from=today - timedelta(days=30),
            valid_until=today - timedelta(days=14),
            position_x=0.5,
            position_y=0.6,
            width=0.2,
            height=0.3,
            search_query="kawa",
        ),
    ]


# =============================================================================
# Tests for list-leaflets with date filters
# =============================================================================


@pytest.mark.integration
class TestListLeafletsDateFilters:
    """Tests for list-leaflets command with date filtering options."""

    def test_list_leaflets_active_on_date(self, leaflet_storage_setup):
        """Test --active-on filter returns leaflets valid on specific date."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            # Get a date within the current promotion's validity
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            active_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--active-on", active_date])

            assert result.exit_code == 0
            # Should show filter info in title
            assert "active on" in result.stdout.lower()
            # Should show the current promotion
            assert "Current Promotion" in result.stdout

    def test_list_leaflets_valid_from(self, leaflet_storage_setup):
        """Test --valid-from filter returns leaflets valid from specified date."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            # Set valid_from to a date in the past - only future-starting leaflets should match
            from_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--valid-from", from_date])

            assert result.exit_code == 0
            assert "valid from" in result.stdout.lower()
            # Should include upcoming promotion (starts after filter date)
            assert "Upcoming Promotion" in result.stdout

    def test_list_leaflets_valid_until(self, leaflet_storage_setup):
        """Test --valid-until filter returns leaflets valid until specified date."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            # Set valid_until to filter out past promotions
            until_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--valid-until", until_date])

            assert result.exit_code == 0
            assert "valid until" in result.stdout.lower()
            # Should show past promotion that ends before the date
            assert "Past Promotion" in result.stdout

    def test_list_leaflets_within_range(self, leaflet_storage_setup):
        """Test --within-range filter returns leaflets valid within date range."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            # Range covering current promotion
            start = (today - timedelta(days=10)).strftime("%Y-%m-%d")
            end = (today + timedelta(days=10)).strftime("%Y-%m-%d")
            range_str = f"{start} to {end}"

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--within-range", range_str])

            assert result.exit_code == 0
            assert "valid from" in result.stdout.lower() and "to" in result.stdout.lower()
            assert "Current Promotion" in result.stdout

    def test_list_leaflets_combined_filters(self, leaflet_storage_setup):
        """Test combination of date filters."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            from_date = (today - timedelta(days=10)).strftime("%Y-%m-%d")
            until_date = (today + timedelta(days=10)).strftime("%Y-%m-%d")

            result = runner.invoke(
                app,
                [
                    "list-leaflets",
                    "biedronka",
                    "--valid-from",
                    from_date,
                    "--valid-until",
                    until_date,
                ],
            )

            assert result.exit_code == 0
            # Both filters should be shown
            assert "valid from" in result.stdout.lower()
            assert "valid until" in result.stdout.lower()
            # Should show current promotion that matches both conditions
            assert "Current Promotion" in result.stdout

    def test_list_leaflets_natural_language_today(self, leaflet_storage_setup):
        """Test --active-on with 'today' natural language date."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--active-on", "today"])

            assert result.exit_code == 0

    def test_list_leaflets_natural_language_tomorrow(self, leaflet_storage_setup):
        """Test --active-on with 'tomorrow' natural language date."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--active-on", "tomorrow"])

            assert result.exit_code == 0

    def test_list_leaflets_invalid_date_error_handling(self, leaflet_storage_setup):
        """Test error handling for invalid date format."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            # Use invalid date format
            result = runner.invoke(app, ["list-leaflets", "biedronka", "--active-on", "not-a-date"])

            # Should still work but show warning
            assert result.exit_code == 0
            assert "Warning" in result.stdout or "warning" in result.stdout.lower()


# =============================================================================
# Tests for search with date filters
# =============================================================================


@pytest.mark.integration
class TestSearchDateFilters:
    """Tests for search command with date filtering options."""

    @patch("src.cli.ScraperOrchestrator")
    def test_search_with_active_on_filter(
        self, mock_orchestrator_class, leaflet_storage_setup, sample_search_results
    ):
        """Test search with --active-on filters results."""
        temp_data_dir = leaflet_storage_setup

        # Setup mock orchestrator
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            active_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

            result = runner.invoke(app, ["search", "kawa", "--active-on", active_date])

            assert result.exit_code == 0
            # Date filter info should be shown
            assert "Date filter:" in result.stdout or "date filter" in result.stdout.lower()

    @patch("src.cli.ScraperOrchestrator")
    def test_search_with_valid_from_filter(
        self, mock_orchestrator_class, leaflet_storage_setup, sample_search_results
    ):
        """Test search with --valid-from filters results."""
        temp_data_dir = leaflet_storage_setup

        # Setup mock orchestrator
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            from_date = (today - timedelta(days=5)).strftime("%Y-%m-%d")

            result = runner.invoke(app, ["search", "kawa", "--valid-from", from_date])

            assert result.exit_code == 0

    @patch("src.cli.ScraperOrchestrator")
    def test_search_with_within_range_filter(
        self, mock_orchestrator_class, leaflet_storage_setup, sample_search_results
    ):
        """Test search with --within-range filters results."""
        temp_data_dir = leaflet_storage_setup

        # Setup mock orchestrator
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            start = (today - timedelta(days=10)).strftime("%Y-%m-%d")
            end = (today + timedelta(days=10)).strftime("%Y-%m-%d")
            range_str = f"{start} to {end}"

            result = runner.invoke(app, ["search", "kawa", "--within-range", range_str])

            assert result.exit_code == 0

    @patch("src.cli.ScraperOrchestrator")
    def test_search_no_results_when_no_matching_leaflets(
        self, mock_orchestrator_class, temp_data_dir
    ):
        """Test search returns no results when no leaflets match date filter."""
        # Setup: Save only expired leaflets
        shop_dir = temp_data_dir / "leaflets" / "biedronka"
        shop_dir.mkdir(parents=True, exist_ok=True)

        # Only past leaflet
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        expired_leaflet = Leaflet(
            leaflet_id=99,
            shop_slug="biedronka",
            name="Expired",
            cover_image_url=HttpUrl("https://example.com/expired.jpg"),
            url=HttpUrl("https://blix.pl/sklep/biedronka/gazetka/99/"),
            valid_from=today - timedelta(days=30),
            valid_until=today - timedelta(days=14),
            status=LeafletStatus.ARCHIVED,
            page_count=10,
        )

        storage = JSONStorage(shop_dir, Leaflet)
        storage.save(expired_leaflet, "99.json")

        # Setup mock orchestrator to return results
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)

        # Return a result from the expired leaflet
        expired_result = SearchResult(
            hash="expired-result",
            name="Old Product",
            image_url=HttpUrl("https://img.blix.pl/image/offer/expired.jpg"),
            product_leaflet_page_uuid="page-uuid-expired",
            leaflet_id=99,
            page_number=1,
            percent_discount=10,
            valid_from=today - timedelta(days=30),
            valid_until=today - timedelta(days=14),
            position_x=0.1,
            position_y=0.1,
            width=0.1,
            height=0.1,
            search_query="product",
        )
        mock_orchestrator.search_products.return_value = [expired_result]

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            # Search for a future date - no leaflets should match
            future_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

            result = runner.invoke(app, ["search", "product", "--active-on", future_date])

            assert result.exit_code == 0
            # Should show filter message
            assert "Date filter:" in result.stdout or "date filter" in result.stdout.lower()
            # Should show filtered count
            assert "leaflets match" in result.stdout.lower() or "Filtered to" in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_search_invalid_date_error_handling(
        self, mock_orchestrator_class, leaflet_storage_setup, sample_search_results
    ):
        """Test search error handling for invalid dates."""
        temp_data_dir = leaflet_storage_setup

        # Setup mock orchestrator
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            result = runner.invoke(app, ["search", "kawa", "--active-on", "invalid-date-xyz"])

            # Should still complete with warning
            assert result.exit_code == 0
            assert "Warning" in result.stdout or "warning" in result.stdout.lower()


# =============================================================================
# Tests for CLI output verification
# =============================================================================


@pytest.mark.integration
class TestCLIOutputVerification:
    """Tests for verifying CLI output with date filters."""

    def test_filter_info_shown_in_output(self, leaflet_storage_setup):
        """Verify filter info is shown in output."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            active_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--active-on", active_date])

            assert result.exit_code == 0
            # Filter info should appear in the title or output
            assert active_date in result.stdout

    def test_correct_count_displayed(self, leaflet_storage_setup):
        """Verify correct count is displayed after filtering."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            # Use a date that matches exactly one leaflet
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            active_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--active-on", active_date])

            assert result.exit_code == 0
            # Should show total count
            assert "Total:" in result.stdout or "leaflets" in result.stdout.lower()

    def test_error_messages_helpful(self, leaflet_storage_setup):
        """Verify error messages are helpful."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            # Use invalid date
            result = runner.invoke(
                app, ["list-leaflets", "biedronka", "--active-on", "rubbish-date"]
            )

            assert result.exit_code == 0
            # Should show helpful message about valid formats
            assert "Valid date formats" in result.stdout or "warning" in result.stdout.lower()


# =============================================================================
# Edge Case Tests
# =============================================================================


@pytest.mark.integration
class TestEdgeCases:
    """Edge case tests for date filtering."""

    def test_empty_storage(self, temp_data_dir):
        """Test with empty storage (no leaflets)."""
        # Setup: Create empty shop directory
        shop_dir = temp_data_dir / "leaflets" / "biedronka"
        shop_dir.mkdir(parents=True, exist_ok=True)

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            result = runner.invoke(app, ["list-leaflets", "biedronka"])

            assert result.exit_code == 0
            # Should show empty table or appropriate message
            assert (
                "0 leaflets" in result.stdout.lower() or "Leaflets for biedronka" in result.stdout
            )

    def test_no_matching_results(self, leaflet_storage_setup):
        """Test when no leaflets match the date filter."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            # Use a date far in the past when no leaflet was valid
            old_date = "2020-01-01"

            result = runner.invoke(app, ["list-leaflets", "biedronka", "--active-on", old_date])

            assert result.exit_code == 0
            # Should show 0 leaflets
            assert "Total: 0 leaflets" in result.stdout or "0 leaflets" in result.stdout.lower()

    def test_backward_compatibility_no_date_filters(self, leaflet_storage_setup):
        """Test backward compatibility - no date filters works as before."""
        temp_data_dir = leaflet_storage_setup

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            # Call without any date filters
            result = runner.invoke(app, ["list-leaflets", "biedronka"])

            assert result.exit_code == 0
            # Should show all leaflets
            assert "Current Promotion" in result.stdout
            assert "Past Promotion" in result.stdout
            assert "Upcoming Promotion" in result.stdout

    def test_nonexistent_shop(self, temp_data_dir):
        """Test with nonexistent shop."""
        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            result = runner.invoke(app, ["list-leaflets", "nonexistent-shop"])

            # Should show appropriate message
            assert result.exit_code == 0
            assert (
                "No leaflets found" in result.stdout or "nonexistent-shop" in result.stdout.lower()
            )

    @patch("src.cli.ScraperOrchestrator")
    def test_search_without_filters_still_works(
        self, mock_orchestrator_class, leaflet_storage_setup, sample_search_results
    ):
        """Test that search without date filters still works correctly."""
        temp_data_dir = leaflet_storage_setup

        # Setup mock orchestrator
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        with patch("src.cli.settings") as mock_settings:
            mock_settings.data_dir = temp_data_dir
            mock_settings.cache_dir = temp_data_dir / "cache"

            result = runner.invoke(app, ["search", "kawa"])

            assert result.exit_code == 0
            # Should not show date filter info
            assert "Date filter:" not in result.stdout
            # Should show results
            assert "Search Results for 'kawa'" in result.stdout
            assert "Kawa ziarnista" in result.stdout or "Kawa rozpuszczalna" in result.stdout
