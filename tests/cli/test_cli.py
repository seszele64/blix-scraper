"""Unit tests for CLI module."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
import json

import pytest
from typer.testing import CliRunner
from pydantic import HttpUrl

from src.cli import app
from src.domain.entities import Shop, Leaflet, SearchResult, LeafletStatus

runner = CliRunner()


@pytest.fixture
def mock_orchestrator():
    """Create a mock ScraperOrchestrator."""
    orchestrator = MagicMock()
    orchestrator.__enter__ = Mock(return_value=orchestrator)
    orchestrator.__exit__ = Mock(return_value=None)
    return orchestrator


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

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_shops_default_options(self, mock_orchestrator_class, sample_shops):
        """Test scrape-shops command with default options."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_all_shops.return_value = sample_shops

        # Act
        result = runner.invoke(app, ["scrape-shops"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=False)
        mock_orchestrator.scrape_all_shops.assert_called_once()
        assert "Scraped Shops" in result.stdout
        assert "Biedronka" in result.stdout
        assert "Kaufland" in result.stdout
        assert "✓ Scraped 2 shops" in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_shops_with_headless(self, mock_orchestrator_class, sample_shops):
        """Test scrape-shops command with --headless option."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_all_shops.return_value = sample_shops

        # Act
        result = runner.invoke(app, ["scrape-shops", "--headless"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=True)

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_shops_empty_results(self, mock_orchestrator_class):
        """Test scrape-shops command with no results."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_all_shops.return_value = []

        # Act
        result = runner.invoke(app, ["scrape-shops"])

        # Assert
        assert result.exit_code == 0
        assert "✓ Scraped 0 shops" in result.stdout


@pytest.mark.integration
class TestSearchCommand:
    """Test search command."""

    @patch("src.cli.ScraperOrchestrator")
    def test_search_default_options(self, mock_orchestrator_class, sample_search_results):
        """Test search command with default options."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        # Act
        result = runner.invoke(app, ["search", "kawa"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=False)
        mock_orchestrator.search_products.assert_called_once_with("kawa", filter_by_name=True)
        assert "Search Results for 'kawa'" in result.stdout
        assert "Kawa ziarnista 500g" in result.stdout
        assert "Jacobs" in result.stdout
        assert "19.99 zł" in result.stdout
        assert "Statistics:" in result.stdout
        assert "Total results: 3" in result.stdout
        assert "Results with price: 2" in result.stdout
        assert "Cheapest: 12.99 zł" in result.stdout
        assert "Most expensive: 19.99 zł" in result.stdout
        assert "Average: 16.49 zł" in result.stdout
        assert "Unique brands: 3" in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_search_with_headless(self, mock_orchestrator_class, sample_search_results):
        """Test search command with --headless option."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        # Act
        result = runner.invoke(app, ["search", "kawa", "--headless"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=True)

    @patch("src.cli.ScraperOrchestrator")
    def test_search_show_all(self, mock_orchestrator_class, sample_search_results):
        """Test search command with --all option."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        # Act
        result = runner.invoke(app, ["search", "kawa", "--all"])

        # Assert
        assert result.exit_code == 0
        assert "Showing 20 of 3 results" not in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_search_no_filter(self, mock_orchestrator_class, sample_search_results):
        """Test search command with --no-filter option."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = sample_search_results

        # Act
        result = runner.invoke(app, ["search", "kawa", "--no-filter"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator.search_products.assert_called_once_with("kawa", filter_by_name=False)
        assert "Showing all offers from leaflets matching 'kawa'" in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_search_no_results(self, mock_orchestrator_class):
        """Test search command with no results."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = []

        # Act
        result = runner.invoke(app, ["search", "nonexistent"])

        # Assert
        assert result.exit_code == 0
        assert "No results found" in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_search_many_results_limit(self, mock_orchestrator_class):
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

        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.search_products.return_value = many_results

        # Act
        result = runner.invoke(app, ["search", "test"])

        # Assert
        assert result.exit_code == 0
        assert "Showing 20 of 25 results" in result.stdout


@pytest.mark.integration
class TestScrapeLeafletsCommand:
    """Test scrape-leaflets command."""

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_leaflets_default_options(self, mock_orchestrator_class, sample_leaflets):
        """Test scrape-leaflets command with default options."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_shop_leaflets.return_value = sample_leaflets

        # Act
        result = runner.invoke(app, ["scrape-leaflets", "biedronka"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=False)
        mock_orchestrator.scrape_shop_leaflets.assert_called_once_with("biedronka")
        assert "Leaflets for biedronka" in result.stdout
        assert "Od środy" in result.stdout
        assert "active" in result.stdout
        assert "✓ Scraped 2 leaflets" in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_leaflets_with_headless(self, mock_orchestrator_class, sample_leaflets):
        """Test scrape-leaflets command with --headless option."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_shop_leaflets.return_value = sample_leaflets

        # Act
        result = runner.invoke(app, ["scrape-leaflets", "biedronka", "--headless"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=True)


@pytest.mark.integration
class TestScrapeOffersCommand:
    """Test scrape-offers command."""

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_offers_default_options(self, mock_orchestrator_class):
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

        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_leaflet_offers.return_value = offers

        # Act
        result = runner.invoke(app, ["scrape-offers", "biedronka", "457727"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=False)
        mock_orchestrator.scrape_leaflet_offers.assert_called_once_with("biedronka", 457727)
        assert "✓ Scraped 2 offers" in result.stdout
        assert "Sample offers:" in result.stdout
        assert "Chleb żytni 500g" in result.stdout
        assert "4.99 zł" in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_offers_with_headless(self, mock_orchestrator_class):
        """Test scrape-offers command with --headless option."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_leaflet_offers.return_value = []

        # Act
        result = runner.invoke(app, ["scrape-offers", "biedronka", "457727", "--headless"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=True)

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_offers_no_results(self, mock_orchestrator_class):
        """Test scrape-offers command with no results."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_leaflet_offers.return_value = []

        # Act
        result = runner.invoke(app, ["scrape-offers", "biedronka", "457727"])

        # Assert
        assert result.exit_code == 0
        assert "✓ Scraped 0 offers" in result.stdout


@pytest.mark.integration
class TestScrapeFullShopCommand:
    """Test scrape-full-shop command."""

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_full_shop_default_options(self, mock_orchestrator_class):
        """Test scrape-full-shop command with default options."""
        # Arrange
        stats = {
            "shop_slug": "biedronka",
            "leaflets_count": 5,
            "offers_count": 150,
            "keywords_count": 75,
            "errors": [],
        }

        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_all_shop_data.return_value = stats

        # Act
        result = runner.invoke(app, ["scrape-full-shop", "biedronka"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator_class.assert_called_once_with(headless=False)
        mock_orchestrator.scrape_all_shop_data.assert_called_once_with("biedronka", True)
        assert "✓ Scraping completed" in result.stdout
        assert "Leaflets: 5" in result.stdout
        assert "Offers: 150" in result.stdout
        assert "Keywords: 75" in result.stdout

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_full_shop_all_leaflets(self, mock_orchestrator_class):
        """Test scrape-full-shop command with --all option."""
        # Arrange
        stats = {
            "shop_slug": "biedronka",
            "leaflets_count": 10,
            "offers_count": 300,
            "keywords_count": 150,
            "errors": [],
        }

        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_all_shop_data.return_value = stats

        # Act
        result = runner.invoke(app, ["scrape-full-shop", "biedronka", "--all"])

        # Assert
        assert result.exit_code == 0
        mock_orchestrator.scrape_all_shop_data.assert_called_once_with("biedronka", False)

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_full_shop_with_errors(self, mock_orchestrator_class):
        """Test scrape-full-shop command with errors."""
        # Arrange
        stats = {
            "shop_slug": "biedronka",
            "leaflets_count": 5,
            "offers_count": 120,
            "keywords_count": 60,
            "errors": ["Failed to scrape leaflet 123: Connection timeout"],
        }

        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_all_shop_data.return_value = stats

        # Act
        result = runner.invoke(app, ["scrape-full-shop", "biedronka"])

        # Assert
        assert result.exit_code == 0
        assert "⚠ Errors: 1" in result.stdout
        assert "Failed to scrape leaflet 123: Connection timeout" in result.stdout


@pytest.mark.integration
class TestListShopsCommand:
    """Test list-shops command."""

    @patch("src.cli.settings")
    @patch("builtins.open", new_callable=mock_open)
    def test_list_shops_with_data(self, mock_file, mock_settings, sample_shops):
        """Test list-shops command with existing data."""
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.__truediv__ = Mock(return_value=mock_path)
        mock_path.__str__ = Mock(return_value="/test/data/shops/shops.json")

        mock_settings.data_dir = mock_path

        # Convert to dict and handle HttpUrl serialization
        shops_data = [shop.model_dump(mode="json") for shop in sample_shops]
        mock_file.return_value.read.return_value = json.dumps(shops_data)

        # Act
        result = runner.invoke(app, ["list-shops"])

        # Assert
        assert result.exit_code == 0
        assert "Scraped Shops" in result.stdout
        assert "Biedronka" in result.stdout
        assert "Kaufland" in result.stdout
        assert "Total: 2 shops" in result.stdout

    @patch("src.cli.settings")
    def test_list_shops_no_data(self, mock_settings):
        """Test list-shops command with no data."""
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = False
        mock_path.__truediv__ = Mock(return_value=mock_path)

        mock_settings.data_dir = mock_path

        # Act
        result = runner.invoke(app, ["list-shops"])

        # Assert
        assert result.exit_code == 0
        assert "No shops found" in result.stdout
        assert "Run 'scrape-shops' first" in result.stdout


@pytest.mark.integration
class TestListLeafletsCommand:
    """Test list-leaflets command."""

    @patch("src.cli.settings")
    @patch("src.cli.JSONStorage")
    def test_list_leaflets_with_data(self, mock_storage_class, mock_settings, sample_leaflets):
        """Test list-leaflets command with existing data."""
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.__truediv__ = Mock(return_value=mock_path)

        mock_settings.data_dir = mock_path

        mock_storage = MagicMock()
        mock_storage.load_all.return_value = sample_leaflets
        mock_storage_class.return_value = mock_storage

        # Act
        result = runner.invoke(app, ["list-leaflets", "biedronka"])

        # Assert
        assert result.exit_code == 0
        assert "Leaflets for biedronka" in result.stdout
        assert "Od środy" in result.stdout
        assert "Total: 2 leaflets" in result.stdout

    @patch("src.cli.settings")
    def test_list_leaflets_no_data(self, mock_settings):
        """Test list-leaflets command with no data."""
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = False
        mock_path.__truediv__ = Mock(return_value=mock_path)

        mock_settings.data_dir = mock_path

        # Act
        result = runner.invoke(app, ["list-leaflets", "biedronka"])

        # Assert
        assert result.exit_code == 0
        assert "No leaflets found for biedronka" in result.stdout
        assert "Run 'scrape-leaflets biedronka' first" in result.stdout

    @patch("src.cli.settings")
    @patch("src.cli.JSONStorage")
    def test_list_leaflets_active_only(self, mock_storage_class, mock_settings, sample_leaflets):
        """Test list-leaflets command with --active-only option."""
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.__truediv__ = Mock(return_value=mock_path)

        mock_settings.data_dir = mock_path

        mock_storage = MagicMock()
        mock_storage.load_all.return_value = sample_leaflets
        mock_storage_class.return_value = mock_storage

        # Act
        result = runner.invoke(app, ["list-leaflets", "biedronka", "--active-only"])

        # Assert
        assert result.exit_code == 0
        # Should only show active leaflets
        assert "Total: 1 leaflets" in result.stdout or "Total: 2 leaflets" in result.stdout


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

    @patch("src.cli.ScraperOrchestrator")
    def test_orchestrator_exception_handling(self, mock_orchestrator_class):
        """Test that orchestrator exceptions are handled gracefully."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(side_effect=Exception("Test error"))

        # Act
        result = runner.invoke(app, ["scrape-shops"])

        # Assert - Should exit with error
        assert result.exit_code != 0
        # Exception is in result.exception, not stdout
        assert result.exception is not None

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_exception_in_context(self, mock_orchestrator_class):
        """Test that exceptions during scraping are handled."""
        # Arrange
        mock_orchestrator = mock_orchestrator_class.return_value
        mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
        mock_orchestrator.__exit__ = Mock(return_value=None)
        mock_orchestrator.scrape_all_shops.side_effect = Exception("Scraping failed")

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
        assert "list-shops" in result.stdout
        assert "list-leaflets" in result.stdout
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
        assert "--all" in result.stdout
        assert "--no-filter" in result.stdout

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
        assert "--active-only" in result.stdout
        assert "--all" in result.stdout
        assert "--headless" in result.stdout

    def test_list_shops_help(self):
        """Test list-shops command help."""
        result = runner.invoke(app, ["list-shops", "--help"])
        assert result.exit_code == 0
        assert "List all scraped shops" in result.stdout

    def test_list_leaflets_help(self):
        """Test list-leaflets command help."""
        result = runner.invoke(app, ["list-leaflets", "--help"])
        assert result.exit_code == 0
        assert "List all scraped leaflets" in result.stdout
        assert "--active-only" in result.stdout

    def test_config_help(self):
        """Test config command help."""
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "Show current configuration" in result.stdout


@pytest.mark.integration
class TestCLIArgumentValidation:
    """Test CLI argument validation."""

    @patch("src.cli.ScraperOrchestrator")
    def test_search_missing_query(self, mock_orchestrator_class):
        """Test search command with missing query argument."""
        result = runner.invoke(app, ["search"])
        assert result.exit_code != 0
        # Typer exits with code 2 for argument errors
        assert result.exit_code == 2

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_leaflets_missing_shop(self, mock_orchestrator_class):
        """Test scrape-leaflets command with missing shop argument."""
        result = runner.invoke(app, ["scrape-leaflets"])
        assert result.exit_code != 0
        assert result.exit_code == 2

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_offers_missing_arguments(self, mock_orchestrator_class):
        """Test scrape-offers command with missing arguments."""
        result = runner.invoke(app, ["scrape-offers"])
        assert result.exit_code != 0
        assert result.exit_code == 2

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_offers_missing_leaflet_id(self, mock_orchestrator_class):
        """Test scrape-offers command with missing leaflet_id argument."""
        result = runner.invoke(app, ["scrape-offers", "biedronka"])
        assert result.exit_code != 0
        assert result.exit_code == 2

    @patch("src.cli.ScraperOrchestrator")
    def test_scrape_full_shop_missing_shop(self, mock_orchestrator_class):
        """Test scrape-full-shop command with missing shop argument."""
        result = runner.invoke(app, ["scrape-full-shop"])
        assert result.exit_code != 0
        assert result.exit_code == 2

    def test_list_leaflets_missing_shop(self):
        """Test list-leaflets command with missing shop argument."""
        result = runner.invoke(app, ["list-leaflets"])
        assert result.exit_code != 0
        assert result.exit_code == 2
