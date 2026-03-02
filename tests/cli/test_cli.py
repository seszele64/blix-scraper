"""Unit tests for CLI module.

Tests the CLI commands:
- scrape-shops
- search
- scrape-leaflets
- scrape-offers
- scrape-full-shop
- config

Note: list-shops and list-leaflets commands were removed in the refactor.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import HttpUrl
from typer.testing import CliRunner

from src.cli import app
from src.domain.entities import Leaflet, LeafletStatus, SearchResult, Shop

runner = CliRunner()


@pytest.fixture
def mock_scraper_service():
    """Create a mock ScraperService."""
    service = MagicMock()
    service.__enter__ = Mock(return_value=service)
    service.__exit__ = Mock(return_value=None)
    return service


@pytest.fixture
def sample_shops():
    """Create sample shop entities."""
    return [
        Shop(
            slug="biedronka",
            brand_id=23,
            name="Biedronka",
            logo_url=HttpUrl("https://img.blix.pl/image/brand/thumbnail_23.jpg"),
            category="Sklepy spożywcze",
            leaflet_count=13,
            is_popular=True,
        ),
        Shop(
            slug="kaufland",
            brand_id=45,
            name="Kaufland",
            logo_url=HttpUrl("https://img.blix.pl/image/brand/thumbnail_45.jpg"),
            category="Sklepy spożywcze",
            leaflet_count=8,
            is_popular=False,
        ),
    ]


@pytest.fixture
def sample_leaflets():
    """Create sample leaflet entities."""
    # Use dynamic dates relative to today to ensure tests work on any date
    today = datetime.now(timezone.utc)
    return [
        Leaflet(
            leaflet_id=457727,
            shop_slug="biedronka",
            name="Od środy - Gazetka promocyjna",
            cover_image_url=HttpUrl("https://imgproxy.blix.pl/image/leaflet/457727/cover.jpg"),
            url=HttpUrl("https://blix.pl/sklep/biedronka/gazetka/457727/"),
            valid_from=today - timedelta(days=7),
            valid_until=today + timedelta(days=7),
            status=LeafletStatus.ACTIVE,
            page_count=12,
        ),
        Leaflet(
            leaflet_id=457728,
            shop_slug="biedronka",
            name="Gazetka archiwalna",
            cover_image_url=HttpUrl("https://imgproxy.blix.pl/image/leaflet/457728/cover.jpg"),
            url=HttpUrl("https://blix.pl/sklep/biedronka/gazetka/457728/"),
            valid_from=today - timedelta(days=30),
            valid_until=today - timedelta(days=14),
            status=LeafletStatus.ARCHIVED,
            page_count=10,
        ),
    ]


@pytest.fixture
def sample_search_results():
    """Create sample search results."""
    # Use dynamic dates relative to today to ensure tests work on any date
    today = datetime.now(timezone.utc)
    valid_from = today - timedelta(days=7)
    valid_until = today + timedelta(days=7)
    return [
        SearchResult(
            hash="abc123",
            name="Kawa ziarnista 500g",
            image_url=HttpUrl("https://img.blix.pl/image/offer/123.jpg"),
            brand_name="Jacobs",
            manufacturer_name="Jacobs Douwe Egberts",
            product_leaflet_page_uuid="page-uuid-1",
            leaflet_id=457727,
            page_number=3,
            price=Decimal("1999"),  # 19.99 PLN in grosz
            percent_discount=20,
            valid_from=valid_from,
            valid_until=valid_until,
            position_x=0.1,
            position_y=0.2,
            width=0.3,
            height=0.4,
            search_query="kawa",
        ),
        SearchResult(
            hash="def456",
            name="Kawa rozpuszczalna 200g",
            image_url=HttpUrl("https://img.blix.pl/image/offer/456.jpg"),
            brand_name="Nescafe",
            manufacturer_name="Nestle",
            product_leaflet_page_uuid="page-uuid-2",
            leaflet_id=457727,
            page_number=5,
            price=Decimal("1299"),  # 12.99 PLN in grosz
            percent_discount=15,
            valid_from=valid_from,
            valid_until=valid_until,
            position_x=0.5,
            position_y=0.6,
            width=0.2,
            height=0.3,
            search_query="kawa",
        ),
        SearchResult(
            hash="ghi789",
            name="Herbata czarna 100 torebek",
            image_url=HttpUrl("https://img.blix.pl/image/offer/789.jpg"),
            brand_name="Lipton",
            manufacturer_name="Unilever",
            product_leaflet_page_uuid="page-uuid-3",
            leaflet_id=457727,
            page_number=7,
            price=None,  # No price
            percent_discount=0,
            valid_from=valid_from,
            valid_until=valid_until,
            position_x=0.7,
            position_y=0.8,
            width=0.15,
            height=0.2,
            search_query="kawa",
        ),
    ]


@pytest.mark.integration
class TestCLIInitialization:
    """Test CLI initialization and app configuration."""

    def test_app_creation(self):
        """Test that the Typer app is created with correct configuration."""
        # Typer app doesn't expose name/help attributes directly
        # Just verify it's a Typer instance
        from typer import Typer

        assert isinstance(app, Typer)

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        from src.cli import main

        assert callable(main)


@pytest.mark.integration
class TestScrapeShopsCommand:
    """Test scrape-shops command."""

    @patch("src.cli.ScraperService")
    def test_scrape_shops_default_options(
        self, mock_service_class, mock_scraper_service, sample_shops
    ):
        """Test scrape-shops command with default options."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_shops.return_value = sample_shops

        # Act
        result = runner.invoke(app, ["scrape-shops"])

        # Assert
        assert result.exit_code == 0
        mock_service_class.assert_called_once_with(headless=False)
        mock_scraper_service.get_shops.assert_called_once()
        assert "Shops" in result.stdout
        assert "Biedronka" in result.stdout
        assert "Kaufland" in result.stdout

    @patch("src.cli.ScraperService")
    def test_scrape_shops_with_headless(
        self, mock_service_class, mock_scraper_service, sample_shops
    ):
        """Test scrape-shops command with --headless option."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_shops.return_value = sample_shops

        # Act
        result = runner.invoke(app, ["scrape-shops", "--headless"])

        # Assert
        assert result.exit_code == 0
        mock_service_class.assert_called_once_with(headless=True)

    @patch("src.cli.ScraperService")
    def test_scrape_shops_empty_results(self, mock_service_class, mock_scraper_service):
        """Test scrape-shops command with no results."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_shops.return_value = []

        # Act
        result = runner.invoke(app, ["scrape-shops"])

        # Assert
        assert result.exit_code == 0
        assert "Total: 0 shops" in result.stdout


@pytest.mark.integration
class TestSearchCommand:
    """Test search command."""

    @patch("src.cli.ScraperService")
    def test_search_default_options(
        self, mock_service_class, mock_scraper_service, sample_search_results
    ):
        """Test search command with default options."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.search.return_value = sample_search_results

        # Act
        result = runner.invoke(app, ["search", "kawa"])

        # Assert
        assert result.exit_code == 0
        mock_service_class.assert_called_once_with(headless=False)
        mock_scraper_service.search.assert_called_once_with(
            query="kawa", filter_by_name=True, date_filter=None
        )
        assert "Search Results" in result.stdout
        assert "Kawa ziarnista 500g" in result.stdout
        assert "19.99 PLN" in result.stdout

    @patch("src.cli.ScraperService")
    def test_search_show_all(self, mock_service_class, mock_scraper_service, sample_search_results):
        """Test search command with --all option."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.search.return_value = sample_search_results

        # Act
        result = runner.invoke(app, ["search", "kawa", "--all"])

        # Assert
        assert result.exit_code == 0
        # With --all, shows all results (no limit message)
        assert "showing 3 of 3" in result.stdout.lower()

    @patch("src.cli.ScraperService")
    def test_search_no_filter(
        self, mock_service_class, mock_scraper_service, sample_search_results
    ):
        """Test search command with --no-filter option."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.search.return_value = sample_search_results

        # Act
        result = runner.invoke(app, ["search", "kawa", "--no-filter"])

        # Assert
        assert result.exit_code == 0
        mock_scraper_service.search.assert_called_once_with(
            query="kawa", filter_by_name=False, date_filter=None
        )

    @patch("src.cli.ScraperService")
    def test_search_no_results(self, mock_service_class, mock_scraper_service):
        """Test search command with no results."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.search.return_value = []

        # Act
        result = runner.invoke(app, ["search", "nonexistent"])

        # Assert
        assert result.exit_code == 0
        # CLI shows empty table for no results
        assert "Search Results" in result.stdout
        assert "showing 0 of 0" in result.stdout.lower()

    @patch("src.cli.ScraperService")
    def test_search_many_results_limit(self, mock_service_class, mock_scraper_service):
        """Test search command with many results (limit to 20)."""
        # Arrange
        # Use dynamic dates relative to today to ensure tests work on any date
        today = datetime.now(timezone.utc)
        valid_from = today - timedelta(days=7)
        valid_until = today + timedelta(days=7)
        many_results = [
            SearchResult(
                hash=f"hash{i}",
                name=f"Product {i}",
                image_url=HttpUrl(f"https://img.blix.pl/image/offer/{i}.jpg"),
                product_leaflet_page_uuid=f"page-uuid-{i}",
                leaflet_id=457727,
                page_number=i,
                price=Decimal(str(i * 100)),
                percent_discount=10,
                valid_from=valid_from,
                valid_until=valid_until,
                position_x=0.1,
                position_y=0.2,
                width=0.3,
                height=0.4,
                search_query="test",
            )
            for i in range(25)
        ]

        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.search.return_value = many_results

        # Act
        result = runner.invoke(app, ["search", "test"])

        # Assert
        assert result.exit_code == 0
        assert "Showing 20 of 25" in result.stdout


@pytest.mark.integration
class TestScrapeLeafletsCommand:
    """Test scrape-leaflets command."""

    @patch("src.cli.ScraperService")
    def test_scrape_leaflets_default_options(
        self, mock_service_class, mock_scraper_service, sample_leaflets
    ):
        """Test scrape-leaflets command with default options."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_leaflets.return_value = sample_leaflets

        # Act
        result = runner.invoke(app, ["scrape-leaflets", "biedronka"])

        # Assert
        assert result.exit_code == 0
        mock_service_class.assert_called_once_with(headless=False)
        mock_scraper_service.get_leaflets.assert_called_once_with("biedronka", date_filter=None)
        assert "Leaflets for biedronka" in result.stdout
        assert "Od środy" in result.stdout
        assert "active" in result.stdout

    @patch("src.cli.ScraperService")
    def test_scrape_leaflets_with_headless(
        self, mock_service_class, mock_scraper_service, sample_leaflets
    ):
        """Test scrape-leaflets command with --headless option."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_leaflets.return_value = sample_leaflets

        # Act
        result = runner.invoke(app, ["scrape-leaflets", "biedronka", "--headless"])

        # Assert
        assert result.exit_code == 0
        mock_service_class.assert_called_once_with(headless=True)


@pytest.mark.integration
class TestScrapeOffersCommand:
    """Test scrape-offers command."""

    @patch("src.cli.ScraperService")
    def test_scrape_offers_default_options(self, mock_service_class, mock_scraper_service):
        """Test scrape-offers command with default options."""
        # Arrange
        from src.domain.entities import Offer

        offers = [
            Offer(
                leaflet_id=457727,
                name="Chleb żytni 500g",
                price=Decimal("4.99"),
                image_url=HttpUrl("https://img.blix.pl/image/offer/123.jpg"),
                page_number=1,
                position_x=0.1,
                position_y=0.2,
                width=0.3,
                height=0.4,
                valid_from=datetime.now(timezone.utc),
                valid_until=datetime.now(timezone.utc),
            ),
            Offer(
                leaflet_id=457727,
                name="Mleko 3.2% 1L",
                price=Decimal("3.49"),
                image_url=HttpUrl("https://img.blix.pl/image/offer/456.jpg"),
                page_number=2,
                position_x=0.5,
                position_y=0.6,
                width=0.2,
                height=0.3,
                valid_from=datetime.now(timezone.utc),
                valid_until=datetime.now(timezone.utc),
            ),
        ]

        # Leaflets needed for the test
        today = datetime.now(timezone.utc)
        leaflets = [
            Leaflet(
                leaflet_id=457727,
                shop_slug="biedronka",
                name="Test Leaflet",
                cover_image_url=HttpUrl("https://example.com/1.jpg"),
                url=HttpUrl("https://blix.pl/1/"),
                valid_from=today - timedelta(days=7),
                valid_until=today + timedelta(days=7),
                status=LeafletStatus.ACTIVE,
                page_count=12,
            ),
        ]

        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_leaflets.return_value = leaflets
        mock_scraper_service.get_offers.return_value = offers

        # Act
        result = runner.invoke(app, ["scrape-offers", "biedronka", "457727"])

        # Assert
        assert result.exit_code == 0
        mock_service_class.assert_called_once_with(headless=False)
        # get_leaflets is called first to find the leaflet
        mock_scraper_service.get_leaflets.assert_called()
        # get_offers is called to get offers from the leaflet
        mock_scraper_service.get_offers.assert_called()
        assert "Offers" in result.stdout
        assert "Chleb żytni 500g" in result.stdout

    @patch("src.cli.ScraperService")
    def test_scrape_offers_with_headless(self, mock_service_class, mock_scraper_service):
        """Test scrape-offers command with --headless option."""
        # Arrange
        today = datetime.now(timezone.utc)
        leaflets = [
            Leaflet(
                leaflet_id=457727,
                shop_slug="biedronka",
                name="Test Leaflet",
                cover_image_url=HttpUrl("https://example.com/1.jpg"),
                url=HttpUrl("https://blix.pl/1/"),
                valid_from=today - timedelta(days=7),
                valid_until=today + timedelta(days=7),
                status=LeafletStatus.ACTIVE,
                page_count=12,
            ),
        ]

        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_leaflets.return_value = leaflets
        mock_scraper_service.get_offers.return_value = []

        # Act
        result = runner.invoke(app, ["scrape-offers", "biedronka", "457727", "--headless"])

        # Assert
        assert result.exit_code == 0
        mock_service_class.assert_called_once_with(headless=True)

    @patch("src.cli.ScraperService")
    def test_scrape_offers_no_results(self, mock_service_class, mock_scraper_service):
        """Test scrape-offers command with no results."""
        # Arrange
        today = datetime.now(timezone.utc)
        leaflets = [
            Leaflet(
                leaflet_id=457727,
                shop_slug="biedronka",
                name="Test Leaflet",
                cover_image_url=HttpUrl("https://example.com/1.jpg"),
                url=HttpUrl("https://blix.pl/1/"),
                valid_from=today - timedelta(days=7),
                valid_until=today + timedelta(days=7),
                status=LeafletStatus.ACTIVE,
                page_count=12,
            ),
        ]

        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_leaflets.return_value = leaflets
        mock_scraper_service.get_offers.return_value = []

        # Act
        result = runner.invoke(app, ["scrape-offers", "biedronka", "457727"])

        # Assert
        assert result.exit_code == 0
        assert "0" in result.stdout or "no" in result.stdout.lower()


@pytest.mark.integration
class TestScrapeFullShopCommand:
    """Test scrape-full-shop command."""

    @patch("src.cli.ScraperService")
    def test_scrape_full_shop_default_options(self, mock_service_class, mock_scraper_service):
        """Test scrape-full-shop command with default options."""
        # Arrange
        # Setup mocks for shops
        shops = [
            Shop(
                slug="biedronka",
                brand_id=23,
                name="Biedronka",
                logo_url=HttpUrl("https://img.blix.pl/image/brand/thumbnail_23.jpg"),
                category="Sklepy spożywcze",
                leaflet_count=13,
                is_popular=True,
            ),
        ]

        today = datetime.now(timezone.utc)
        leaflets = [
            Leaflet(
                leaflet_id=457727,
                shop_slug="biedronka",
                name="Test",
                cover_image_url=HttpUrl("https://example.com/1.jpg"),
                url=HttpUrl("https://blix.pl/1/"),
                valid_from=today - timedelta(days=7),
                valid_until=today + timedelta(days=7),
                status=LeafletStatus.ACTIVE,
                page_count=12,
            ),
        ]

        # Create mock offers and keywords
        from src.domain.entities import Keyword, Offer

        offers = [
            Offer(
                leaflet_id=457727,
                name="Product 1",
                price=Decimal("10.00"),
                image_url=HttpUrl("https://example.com/o1.jpg"),
                page_number=1,
                position_x=0.1,
                position_y=0.2,
                width=0.3,
                height=0.4,
                valid_from=today,
                valid_until=today,
            ),
        ]

        keywords = [
            Keyword(
                leaflet_id=457727,
                text="Nabiał",
                url="/sklep/biedronka/keywords/nabial",
                category_path="Oferty > Nabiał",
            ),
        ]

        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_shops.return_value = shops
        mock_scraper_service.get_leaflets.return_value = leaflets
        mock_scraper_service.get_offers.return_value = offers
        mock_scraper_service.get_keywords.return_value = keywords

        # Act
        result = runner.invoke(app, ["scrape-full-shop", "biedronka"])

        # Assert
        assert result.exit_code == 0
        mock_service_class.assert_called_once_with(headless=False)
        # Verify get_shops was called
        mock_scraper_service.get_shops.assert_called()
        # Verify get_leaflets was called
        mock_scraper_service.get_leaflets.assert_called()

    @patch("src.cli.ScraperService")
    def test_scrape_full_shop_with_errors(self, mock_service_class, mock_scraper_service):
        """Test scrape-full-shop command handles errors gracefully."""
        # Arrange
        shops = [
            Shop(
                slug="biedronka",
                brand_id=23,
                name="Biedronka",
                logo_url=HttpUrl("https://img.blix.pl/image/brand/thumbnail_23.jpg"),
                category="Sklepy spożywcze",
                leaflet_count=13,
                is_popular=True,
            ),
        ]

        today = datetime.now(timezone.utc)
        leaflets = [
            Leaflet(
                leaflet_id=457727,
                shop_slug="biedronka",
                name="Test",
                cover_image_url=HttpUrl("https://example.com/1.jpg"),
                url=HttpUrl("https://blix.pl/1/"),
                valid_from=today - timedelta(days=7),
                valid_until=today + timedelta(days=7),
                status=LeafletStatus.ACTIVE,
                page_count=12,
            ),
        ]

        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_shops.return_value = shops
        mock_scraper_service.get_leaflets.return_value = leaflets
        # Simulate error when getting offers
        mock_scraper_service.get_offers.side_effect = Exception("Network error")
        mock_scraper_service.get_keywords.return_value = []

        # Act
        result = runner.invoke(app, ["scrape-full-shop", "biedronka"])

        # Assert - should still complete but with warnings
        assert result.exit_code == 0


@pytest.mark.integration
class TestConfigCommand:
    """Test config command."""

    @patch("src.cli.settings")
    def test_config_command(self, mock_settings):
        """Test config command displays configuration."""
        # Arrange

        mock_path = MagicMock(spec=Path)
        mock_path.__str__ = Mock(return_value="/test/data")
        mock_settings.data_dir = mock_path
        mock_settings.base_url = "https://test.blix.pl"
        mock_settings.headless = True
        mock_settings.request_delay_min = 0.5
        mock_settings.request_delay_max = 1.0
        mock_settings.log_level = "INFO"
        mock_settings.log_format = "console"

        # Act
        result = runner.invoke(app, ["config"])

        # Assert
        assert result.exit_code == 0
        assert "Configuration" in result.stdout
        assert "Data Directory" in result.stdout
        assert "Base URL" in result.stdout
        assert "Headless" in result.stdout
        assert "Request Delay" in result.stdout
        assert "Log Level" in result.stdout
        assert "Log Format" in result.stdout


@pytest.mark.integration
class TestCLIErrorHandling:
    """Test CLI error handling."""

    @patch("src.cli.ScraperService")
    def test_service_exception_handling(self, mock_service_class):
        """Test that service exceptions are handled gracefully."""
        # Arrange
        mock_service = MagicMock()
        mock_service.__enter__ = Mock(side_effect=Exception("Test error"))
        mock_service_class.return_value = mock_service

        # Act
        result = runner.invoke(app, ["scrape-shops"])

        # Assert - Should exit with error
        assert result.exit_code != 0
        # Exception is in result.exception, not stdout
        assert result.exception is not None

    @patch("src.cli.ScraperService")
    def test_scrape_exception_in_context(self, mock_service_class, mock_scraper_service):
        """Test that exceptions during scraping are handled."""
        # Arrange
        mock_service_class.return_value = mock_scraper_service
        mock_scraper_service.get_shops.side_effect = Exception("Scraping failed")

        # Act
        result = runner.invoke(app, ["scrape-shops"])

        # Assert
        assert result.exit_code != 0
        assert result.exception is not None


@pytest.mark.integration
class TestCLIHelp:
    """Test CLI help functionality."""

    def test_main_help(self):
        """Test that main help is displayed."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "blix-scraper" in result.stdout
        assert "scrape-shops" in result.stdout
        assert "search" in result.stdout
        assert "scrape-leaflets" in result.stdout
        assert "scrape-offers" in result.stdout
        assert "scrape-full-shop" in result.stdout
        assert "config" in result.stdout

    def test_scrape_shops_help(self):
        """Test scrape-shops command help."""
        result = runner.invoke(app, ["scrape-shops", "--help"])
        assert result.exit_code == 0
        assert "Scrape all shops" in result.stdout
        assert "--headless" in result.stdout

    def test_search_help(self):
        """Test search command help."""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
        assert "Search for products" in result.stdout
        assert "--headless" in result.stdout

    def test_scrape_leaflets_help(self):
        """Test scrape-leaflets command help."""
        result = runner.invoke(app, ["scrape-leaflets", "--help"])
        assert result.exit_code == 0
        assert "Scrape all leaflets" in result.stdout
        assert "--headless" in result.stdout

    def test_scrape_offers_help(self):
        """Test scrape-offers command help."""
        result = runner.invoke(app, ["scrape-offers", "--help"])
        assert result.exit_code == 0
        assert "Scrape offers" in result.stdout
        assert "--headless" in result.stdout

    def test_scrape_full_shop_help(self):
        """Test scrape-full-shop command help."""
        result = runner.invoke(app, ["scrape-full-shop", "--help"])
        assert result.exit_code == 0
        assert "Scrape all data" in result.stdout

    def test_config_help(self):
        """Test config command help."""
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "Show current configuration" in result.stdout


@pytest.mark.integration
class TestCLIArgumentValidation:
    """Test CLI argument validation."""

    def test_search_missing_query(self):
        """Test search command with missing query argument."""
        result = runner.invoke(app, ["search"])
        assert result.exit_code != 0
        # Typer exits with code 2 for argument errors
        assert result.exit_code == 2

    def test_scrape_leaflets_missing_shop(self):
        """Test scrape-leaflets command with missing shop argument."""
        result = runner.invoke(app, ["scrape-leaflets"])
        assert result.exit_code != 0
        assert result.exit_code == 2

    def test_scrape_offers_missing_arguments(self):
        """Test scrape-offers command with missing arguments."""
        result = runner.invoke(app, ["scrape-offers"])
        assert result.exit_code != 0
        assert result.exit_code == 2

    def test_scrape_offers_missing_leaflet_id(self):
        """Test scrape-offers command with missing leaflet_id argument."""
        result = runner.invoke(app, ["scrape-offers", "biedronka"])
        assert result.exit_code != 0
        assert result.exit_code == 2

    def test_scrape_full_shop_missing_shop(self):
        """Test scrape-full-shop command with missing shop argument."""
        result = runner.invoke(app, ["scrape-full-shop"])
        assert result.exit_code != 0
        assert result.exit_code == 2
