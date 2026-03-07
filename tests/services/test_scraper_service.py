"""Unit tests for ScraperService.

Tests cover:
- Context manager behavior (WebDriver lifecycle)
- get_shops method
- get_leaflets method with date filtering
- get_offers method
- get_keywords method
- search method
- Error handling
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import HttpUrl
from selenium.webdriver.remote.webdriver import WebDriver

from src.domain.date_filter import DateFilterOptions
from src.domain.entities import Keyword, Leaflet, LeafletStatus, Offer, SearchResult, Shop
from src.services.scraper_service import ScraperService


@pytest.fixture
def mock_driver():
    """Create a mock WebDriver."""
    driver = Mock(spec=WebDriver)
    driver.get = Mock()
    driver.quit = Mock()
    driver.current_url = "https://test.blix.pl"
    driver.page_source = "<html><body>Test</body></html>"
    return driver


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
    ]


@pytest.fixture
def sample_offers():
    """Create sample offer entities."""
    today = datetime.now(timezone.utc)
    return [
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
            valid_from=today - timedelta(days=7),
            valid_until=today + timedelta(days=7),
        ),
    ]


@pytest.fixture
def sample_keywords():
    """Create sample keyword entities."""
    return [
        Keyword(
            leaflet_id=457727,
            text="Nabiał",
            url="/sklep/biedronka/keywords/nabial",
            category_path="Oferty > Nabiał",
        ),
        Keyword(
            leaflet_id=457727,
            text="Owoce",
            url="/sklep/biedronka/keywords/owoce",
            category_path="Oferty > Owoce",
        ),
    ]


@pytest.fixture
def sample_search_results():
    """Create sample search result entities."""
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
    ]


@pytest.mark.unit
class TestScraperServiceContextManager:
    """Tests for ScraperService context manager behavior."""

    @patch("src.services.scraper_service.DriverFactory")
    def test_service_context_manager_creates_driver(self, mock_driver_factory, mock_driver):
        """Verify WebDriver is created and cleaned up."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver

        # Act
        with ScraperService(headless=True) as service:
            # Assert - driver should be created
            mock_driver_factory.create_driver.assert_called_once_with(headless=True)
            assert service._driver is not None

        # Assert - driver should be cleaned up
        mock_driver.quit.assert_called_once()

    @patch("src.services.scraper_service.DriverFactory")
    def test_service_context_manager_handles_driver_creation_failure(self, mock_driver_factory):
        """Verify error handling when driver creation fails."""
        # Arrange
        mock_driver_factory.create_driver.side_effect = Exception("Driver creation failed")

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            with ScraperService():
                pass

        assert "Failed to initialize WebDriver" in str(exc_info.value)

    @patch("src.services.scraper_service.DriverFactory")
    def test_service_context_manager_handles_cleanup_failure(
        self, mock_driver_factory, mock_driver
    ):
        """Verify error handling when driver cleanup fails."""
        # Arrange
        mock_driver.quit.side_effect = Exception("Cleanup failed")
        mock_driver_factory.create_driver.return_value = mock_driver

        # Act & Assert - should not raise, just log warning
        with ScraperService():
            pass

        mock_driver.quit.assert_called_once()


@pytest.mark.unit
class TestScraperServiceGetters:
    """Tests for ScraperService getter methods."""

    @patch("src.services.scraper_service.DriverFactory")
    def test_get_shops_returns_list(self, mock_driver_factory, mock_driver, sample_shops):
        """Mock ShopScraper, verify returns list of Shop."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = sample_shops

        with patch("src.services.scraper_service.ShopScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act
                result = service.get_shops()

                # Assert
                assert result == sample_shops
                assert len(result) == 2
                mock_scraper_class.assert_called_once_with(mock_driver)
                mock_scraper.scrape.assert_called_once()

    @patch("src.services.scraper_service.DriverFactory")
    def test_get_leaflets_with_date_filter(self, mock_driver_factory, mock_driver, sample_leaflets):
        """Mock LeafletScraper, verify date filtering works."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = sample_leaflets

        # Create date filter for specific date
        filter_date = datetime.now(timezone.utc)
        date_filter = DateFilterOptions(active_on=filter_date)

        with patch("src.services.scraper_service.LeafletScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act
                service.get_leaflets("biedronka", date_filter=date_filter)

                # Assert
                mock_scraper_class.assert_called_once_with(mock_driver, shop_slug="biedronka")
                mock_scraper.scrape.assert_called_once()

    @patch("src.services.scraper_service.DriverFactory")
    def test_get_leaflets_without_date_filter(
        self, mock_driver_factory, mock_driver, sample_leaflets
    ):
        """Mock LeafletScraper, verify returns all leaflets without filtering."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = sample_leaflets

        with patch("src.services.scraper_service.LeafletScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act
                result = service.get_leaflets("biedronka")

                # Assert
                assert result == sample_leaflets

    @patch("src.services.scraper_service.DriverFactory")
    def test_get_offers_returns_list(
        self, mock_driver_factory, mock_driver, sample_leaflets, sample_offers
    ):
        """Mock OfferScraper, verify returns offers."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = sample_offers

        with patch("src.services.scraper_service.OfferScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act
                result = service.get_offers("biedronka", sample_leaflets[0])

                # Assert
                assert result == sample_offers
                assert len(result) == 1
                # Verify leaflet is linked to offer
                assert result[0].leaflet == sample_leaflets[0]
                mock_scraper_class.assert_called_once_with(
                    mock_driver, leaflet_id=sample_leaflets[0].leaflet_id
                )

    @patch("src.services.scraper_service.DriverFactory")
    def test_get_keywords_returns_list(
        self, mock_driver_factory, mock_driver, sample_leaflets, sample_keywords
    ):
        """Mock KeywordScraper, verify returns keywords."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = sample_keywords

        with patch("src.services.scraper_service.KeywordScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act
                result = service.get_keywords("biedronka", sample_leaflets[0])

                # Assert
                assert result == sample_keywords
                assert len(result) == 2
                mock_scraper_class.assert_called_once_with(
                    mock_driver, leaflet_id=sample_leaflets[0].leaflet_id
                )

    @patch("src.services.scraper_service.DriverFactory")
    def test_search_returns_results(self, mock_driver_factory, mock_driver, sample_search_results):
        """Mock SearchScraper, verify returns search results."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = sample_search_results

        with patch("src.services.scraper_service.SearchScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act
                result = service.search("kawa", filter_by_name=True)

                # Assert
                assert result == sample_search_results
                assert len(result) == 1
                mock_scraper_class.assert_called_once_with(
                    mock_driver, search_query="kawa", filter_by_name=True
                )

    @patch("src.services.scraper_service.DriverFactory")
    def test_search_with_date_filter(self, mock_driver_factory, mock_driver, sample_search_results):
        """Mock SearchScraper, verify date filtering works for search."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = sample_search_results

        filter_date = datetime.now(timezone.utc)
        date_filter = DateFilterOptions(active_on=filter_date)

        with patch("src.services.scraper_service.SearchScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act
                result = service.search("kawa", filter_by_name=True, date_filter=date_filter)

                # Assert
                assert result == sample_search_results


@pytest.mark.unit
class TestScraperServiceErrorHandling:
    """Tests for ScraperService error handling."""

    @patch("src.services.scraper_service.DriverFactory")
    def test_error_handling_get_shops(self, mock_driver_factory, mock_driver):
        """Verify errors are logged and re-raised for get_shops."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.side_effect = Exception("Network error")

        with patch("src.services.scraper_service.ShopScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act & Assert
                with pytest.raises(Exception) as exc_info:
                    service.get_shops()

                assert "Network error" in str(exc_info.value)

    @patch("src.services.scraper_service.DriverFactory")
    def test_error_handling_get_leaflets(self, mock_driver_factory, mock_driver):
        """Verify errors are logged and re-raised for get_leaflets."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.side_effect = Exception("Parse error")

        with patch("src.services.scraper_service.LeafletScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act & Assert
                with pytest.raises(Exception) as exc_info:
                    service.get_leaflets("biedronka")

                assert "Parse error" in str(exc_info.value)

    @patch("src.services.scraper_service.DriverFactory")
    def test_error_handling_get_offers(self, mock_driver_factory, mock_driver, sample_leaflets):
        """Verify errors are logged and re-raised for get_offers."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.side_effect = Exception("Scraping failed")

        with patch("src.services.scraper_service.OfferScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act & Assert
                with pytest.raises(Exception) as exc_info:
                    service.get_offers("biedronka", sample_leaflets[0])

                assert "Scraping failed" in str(exc_info.value)

    @patch("src.services.scraper_service.DriverFactory")
    def test_error_handling_search(self, mock_driver_factory, mock_driver):
        """Verify errors are logged and re-raised for search."""
        # Arrange
        mock_driver_factory.create_driver.return_value = mock_driver
        mock_scraper = MagicMock()
        mock_scraper.scrape.side_effect = Exception("Search error")

        with patch("src.services.scraper_service.SearchScraper") as mock_scraper_class:
            mock_scraper_class.return_value = mock_scraper

            with ScraperService() as service:
                # Act & Assert
                with pytest.raises(Exception) as exc_info:
                    service.search("test")

                assert "Search error" in str(exc_info.value)

    @patch("src.services.scraper_service.DriverFactory")
    def test_driver_not_initialized_error(self, mock_driver_factory):
        """Verify proper error when accessing driver without context manager."""
        # Arrange
        service = ScraperService()

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            _ = service.driver

        assert "WebDriver not initialized" in str(exc_info.value)
