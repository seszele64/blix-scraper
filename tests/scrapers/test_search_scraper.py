"""Tests for SearchScraper."""

import json
from decimal import Decimal
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.scrapers.search_scraper import SearchScraper


@pytest.mark.integration
@pytest.mark.scraping
class TestSearchScraper:
    """Tests for SearchScraper class."""

    def test_initialization(self, mock_driver):
        """Test SearchScraper initialization."""
        scraper = SearchScraper(mock_driver, "chleb", filter_by_name=True)

        assert scraper.driver == mock_driver
        assert scraper.search_query == "chleb"
        assert scraper.filter_by_name is True
        assert scraper.leaflet_shop_map == {}

    def test_initialization_without_filter(self, mock_driver):
        """Test SearchScraper initialization without name filtering."""
        scraper = SearchScraper(mock_driver, "mleko", filter_by_name=False)

        assert scraper.filter_by_name is False

    def test_wait_for_content(self, mock_driver):
        """Test waiting for search results to load."""
        scraper = SearchScraper(mock_driver, "test")

        with patch("src.scrapers.search_scraper.human_delay"):
            with patch("src.scrapers.search_scraper.wait_for_element"):
                scraper._wait_for_content()

    def test_wait_for_content_timeout(self, mock_driver):
        """Test waiting for content when element not found."""
        scraper = SearchScraper(mock_driver, "test")

        with patch("src.scrapers.search_scraper.human_delay"):
            with patch(
                "src.scrapers.search_scraper.wait_for_element", side_effect=Exception("Timeout")
            ):
                # Should not raise, just log debug
                scraper._wait_for_content()

    def test_extract_leaflet_shop_map_from_swiper(self, mock_driver):
        """Test extracting leaflet to shop mapping from swiper slides."""
        html = """
        <html>
            <body>
                <div class="swiper-slide">
                    <div class="page-wrapper" data-leaflet-id="458087" data-brand-name="Lidl"></div>
                </div>
                <div class="swiper-slide">
                    <div class="page-wrapper" data-leaflet-id="457928" data-brand-name="Biedronka"></div>
                </div>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "test")
        scraper._extract_leaflet_shop_map(soup)

        assert len(scraper.leaflet_shop_map) == 2
        assert scraper.leaflet_shop_map[458087] == "Lidl"
        assert scraper.leaflet_shop_map[457928] == "Biedronka"

    def test_extract_leaflet_shop_map_from_items(self, mock_driver):
        """Test extracting leaflet to shop mapping from leaflet items."""
        html = """
        <html>
            <body>
                <div class="leaflet" data-leaflet-id="457928" data-brand-name="Stokrotka"></div>
                <div class="leaflet" data-leaflet-id="457929" data-brand-name="Kaufland"></div>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "test")
        scraper._extract_leaflet_shop_map(soup)

        assert len(scraper.leaflet_shop_map) == 2
        assert scraper.leaflet_shop_map[457928] == "Stokrotka"
        assert scraper.leaflet_shop_map[457929] == "Kaufland"

    def test_extract_leaflet_shop_map_swiper_priority(self, mock_driver):
        """Test that swiper slides have priority over leaflet items."""
        html = """  # noqa: E501
        <html>
            <body>
                <div class="swiper-slide">
                    <div class="page-wrapper" data-leaflet-id="457928" data-brand-name="Biedronka"></div>
                </div>
                <div class="leaflet" data-leaflet-id="457928" data-brand-name="Stokrotka"></div>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "test")
        scraper._extract_leaflet_shop_map(soup)

        assert len(scraper.leaflet_shop_map) == 1
        assert scraper.leaflet_shop_map[457928] == "Biedronka"

    def test_extract_leaflet_shop_map_invalid_id(self, mock_driver):
        """Test handling invalid leaflet ID."""
        html = """  # noqa: E501
        <html>
            <body>
                <div class="swiper-slide">
                    <div class="page-wrapper" data-leaflet-id="invalid" data-brand-name="Test"></div>
                </div>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "test")
        scraper._extract_leaflet_shop_map(soup)

        assert len(scraper.leaflet_shop_map) == 0

    def test_extract_entities_with_window_offers(self, mock_driver):
        """Test extracting search results from window.offers."""
        offers_data = [
            {
                "name": "Chleb żytni",
                "image": "https://example.com/image1.jpg",
                "leafletId": 457928,
                "pageNumber": 1,
                "productLeafletPageUuid": "uuid-1",
                "dateStart": {"date": "2025-10-29T00:00:00Z"},
                "dateEnd": {"date": "2025-11-05T23:59:59Z"},
                "price": 499,
                "percentDiscount": 20,
                "area": {
                    "topLeftCorner": {"x": 0.1, "y": 0.2},
                    "bottomRightCorner": {"x": 0.3, "y": 0.4},
                },
                "hash": "abc123",
            }
        ]

        html = f"""
        <html>
            <body>
                <script>
                    window.offers = {json.dumps(offers_data)};
                </script>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "chleb")
        results = scraper._extract_entities(soup, "https://blix.pl/szukaj/?szukaj=chleb")

        assert len(results) == 1
        assert results[0].name == "Chleb żytni"
        assert results[0].hash == "abc123"
        assert results[0].price == Decimal("499")

    def test_extract_entities_no_window_offers(self, mock_driver):
        """Test extracting when no window.offers found."""
        html = """
        <html>
            <body>
                <div class="offer-list">No offers</div>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "test")
        results = scraper._extract_entities(soup, "https://blix.pl/szukaj/?szukaj=test")

        assert len(results) == 0

    def test_extract_entities_json_decode_error(self, mock_driver):
        """Test handling JSON decode error."""
        html = """
        <html>
            <body>
                <script>
                    window.offers = invalid json;
                </script>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "test")
        results = scraper._extract_entities(soup, "https://blix.pl/szukaj/?szukaj=test")

        assert len(results) == 0

    def test_extract_entities_with_filtering(self, mock_driver):
        """Test extracting with name filtering enabled."""
        offers_data = [
            {
                "name": "Chleb żytni",
                "image": "https://example.com/image1.jpg",
                "leafletId": 457928,
                "pageNumber": 1,
                "productLeafletPageUuid": "uuid-1",
                "dateStart": {"date": "2025-10-29T00:00:00Z"},
                "dateEnd": {"date": "2025-11-05T23:59:59Z"},
                "hash": "abc123",
            },
            {
                "name": "Mleko UHT",
                "image": "https://example.com/image2.jpg",
                "leafletId": 457928,
                "pageNumber": 2,
                "productLeafletPageUuid": "uuid-2",
                "dateStart": {"date": "2025-10-29T00:00:00Z"},
                "dateEnd": {"date": "2025-11-05T23:59:59Z"},
                "hash": "def456",
            },
        ]

        html = f"""
        <html>
            <body>
                <script>
                    window.offers = {json.dumps(offers_data)};
                </script>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "chleb", filter_by_name=True)
        results = scraper._extract_entities(soup, "https://blix.pl/szukaj/?szukaj=chleb")

        assert len(results) == 1
        assert results[0].name == "Chleb żytni"

    def test_extract_entities_without_filtering(self, mock_driver):
        """Test extracting without name filtering."""
        offers_data = [
            {
                "name": "Chleb żytni",
                "image": "https://example.com/image1.jpg",
                "leafletId": 457928,
                "pageNumber": 1,
                "productLeafletPageUuid": "uuid-1",
                "dateStart": {"date": "2025-10-29T00:00:00Z"},
                "dateEnd": {"date": "2025-11-05T23:59:59Z"},
                "hash": "abc123",
            },
            {
                "name": "Mleko UHT",
                "image": "https://example.com/image2.jpg",
                "leafletId": 457928,
                "pageNumber": 2,
                "productLeafletPageUuid": "uuid-2",
                "dateStart": {"date": "2025-10-29T00:00:00Z"},
                "dateEnd": {"date": "2025-11-05T23:59:59Z"},
                "hash": "def456",
            },
        ]

        html = f"""
        <html>
            <body>
                <script>
                    window.offers = {json.dumps(offers_data)};
                </script>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = SearchScraper(mock_driver, "test", filter_by_name=False)
        results = scraper._extract_entities(soup, "https://blix.pl/szukaj/?szukaj=test")

        assert len(results) == 2

    def test_matches_query_single_word(self, mock_driver):
        """Test matching single word query."""
        scraper = SearchScraper(mock_driver, "chleb")

        assert scraper._matches_query("Chleb żytni") is True
        assert scraper._matches_query("Chleb pszenny") is True
        assert scraper._matches_query("Mleko") is False

    def test_matches_query_multi_word(self, mock_driver):
        """Test matching multi-word query."""
        scraper = SearchScraper(mock_driver, "chleb żytni")

        assert scraper._matches_query("Chleb żytni 500g") is True
        assert scraper._matches_query("Chleb żytni pełnoziarnisty") is True
        assert scraper._matches_query("Chleb pszenny") is False
        assert scraper._matches_query("Mleko żytni") is False

    def test_matches_query_case_insensitive(self, mock_driver):
        """Test case-insensitive matching."""
        scraper = SearchScraper(mock_driver, "CHLEB")

        assert scraper._matches_query("chleb") is True
        assert scraper._matches_query("Chleb") is True
        assert scraper._matches_query("CHLEB") is True

    def test_matches_query_whitespace(self, mock_driver):
        """Test matching with whitespace handling."""
        scraper = SearchScraper(mock_driver, "  chleb  ")

        assert scraper._matches_query("  Chleb żytni  ") is True

    def test_parse_product_success(self, mock_driver):
        """Test successful product parsing."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
            "price": 499,
            "percentDiscount": 20,
            "manufacturerName": "Manufacturer",
            "brandName": "Brand",
            "hash": "abc123",
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is not None
        assert result.name == "Chleb żytni"
        assert result.hash == "abc123"
        assert result.price == Decimal("499")
        assert result.percent_discount == 20
        assert result.manufacturer_name == "Manufacturer"
        assert result.brand_name == "Brand"

    def test_parse_product_missing_required_field(self, mock_driver):
        """Test parsing product with missing required field."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            # Missing productLeafletPageUuid
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is None

    def test_parse_product_date_parse_error(self, mock_driver):
        """Test parsing product with invalid date."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "invalid-date"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is None

    def test_parse_product_string_dates(self, mock_driver):
        """Test parsing product with string dates instead of objects."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": "2025-10-29T00:00:00Z",
            "dateEnd": "2025-11-05T23:59:59Z",
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is not None
        assert result.valid_from.tzinfo is not None
        assert result.valid_until.tzinfo is not None

    def test_parse_product_with_area(self, mock_driver):
        """Test parsing product with position area."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
            "area": {
                "topLeftCorner": {"x": 0.1, "y": 0.2},
                "bottomRightCorner": {"x": 0.5, "y": 0.6},
            },
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is not None
        assert result.position_x == 0.1
        assert result.position_y == 0.2
        assert result.width == pytest.approx(0.4)
        assert result.height == pytest.approx(0.4)

    def test_parse_product_without_area(self, mock_driver):
        """Test parsing product without position area."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is not None
        assert result.position_x == 0.0
        assert result.position_y == 0.0
        assert result.width == 1.0
        assert result.height == 1.0

    def test_parse_product_with_price(self, mock_driver):
        """Test parsing product with price."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
            "price": 499,
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is not None
        assert result.price == Decimal("499")

    def test_parse_product_without_price(self, mock_driver):
        """Test parsing product without price."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is not None
        assert result.price is None

    def test_parse_product_generate_hash(self, mock_driver):
        """Test generating hash when not provided."""
        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
        }

        scraper = SearchScraper(mock_driver, "chleb")
        result = scraper._parse_product(data)

        assert result is not None
        assert result.hash is not None
        assert len(result.hash) == 9  # MD5 hash truncated to 9 chars

    def test_parse_product_with_shop_mapping(self, mock_driver):
        """Test parsing product with shop name from mapping."""
        scraper = SearchScraper(mock_driver, "chleb")
        scraper.leaflet_shop_map[457928] = "Biedronka"

        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
        }

        result = scraper._parse_product(data)

        assert result is not None
        assert result.shop_name == "Biedronka"

    def test_parse_product_without_shop_mapping(self, mock_driver):
        """Test parsing product without shop name mapping."""
        scraper = SearchScraper(mock_driver, "chleb")

        data = {
            "name": "Chleb żytni",
            "image": "https://example.com/image.jpg",
            "leafletId": 457928,
            "pageNumber": 1,
            "productLeafletPageUuid": "uuid-123",
            "dateStart": {"date": "2025-10-29T00:00:00Z"},
            "dateEnd": {"date": "2025-11-05T23:59:59Z"},
        }

        result = scraper._parse_product(data)

        assert result is not None
        assert result.shop_name is None

    def test_scrape_success(self, mock_driver):
        """Test successful scraping workflow."""
        offers_data = [
            {
                "name": "Chleb żytni",
                "image": "https://example.com/image.jpg",
                "leafletId": 457928,
                "pageNumber": 1,
                "productLeafletPageUuid": "uuid-123",
                "dateStart": {"date": "2025-10-29T00:00:00Z"},
                "dateEnd": {"date": "2025-11-05T23:59:59Z"},
                "hash": "abc123",
            }
        ]

        html = f"""
        <html>
            <body>
                <script>
                    window.offers = {json.dumps(offers_data)};
                </script>
            </body>
        </html>
        """

        mock_driver.page_source = html

        with patch("src.scrapers.search_scraper.human_delay"):
            scraper = SearchScraper(mock_driver, "chleb")
            results = scraper.scrape("https://blix.pl/szukaj/?szukaj=chleb")

        assert len(results) == 1
        assert results[0].name == "Chleb żytni"
        mock_driver.get.assert_called_once_with("https://blix.pl/szukaj/?szukaj=chleb")

    def test_scrape_error_handling(self, mock_driver):
        """Test error handling during scraping."""
        mock_driver.get.side_effect = Exception("Network error")

        scraper = SearchScraper(mock_driver, "chleb")

        with pytest.raises(Exception, match="Network error"):
            scraper.scrape("https://blix.pl/szukaj/?szukaj=chleb")
