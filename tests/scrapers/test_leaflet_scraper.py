"""Tests for LeafletScraper."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.domain.entities import LeafletStatus
from src.scrapers.leaflet_scraper import LeafletScraper


@pytest.mark.integration
@pytest.mark.scraping
class TestLeafletScraper:
    """Tests for LeafletScraper class."""

    def test_initialization(self, mock_driver):
        """Test LeafletScraper initialization."""
        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")

        assert scraper.driver == mock_driver
        assert scraper.shop_slug == "biedronka"

    def test_wait_for_content(self, mock_driver):
        """Test waiting for leaflet items to load."""
        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")

        with patch("src.scrapers.leaflet_scraper.wait_for_element"):
            scraper._wait_for_content()

    def test_should_scroll(self, mock_driver):
        """Test that leaflet scraper should scroll."""
        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")

        assert scraper._should_scroll() is True

    def test_extract_entities_success(self, mock_driver):
        """Test extracting multiple leaflets from HTML."""
        html = """
        <div class="section-n__items--leaflets">
            <div class="leaflet section-n__item"
                 data-leaflet-id="457727"
                 data-leaflet-name="Od środy"
                 data-date-start="2025-10-29T00:00:00"
                 data-date-end="2025-11-05T23:59:59">
                <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
                <div class="leaflet__cover">
                    <img src="https://imgproxy.blix.pl/image/leaflet/457727/cover.jpg" />
                </div>
            </div>
            <div class="leaflet section-n__item"
                 data-leaflet-id="457728"
                 data-leaflet-name="Od poniedziałku"
                 data-date-start="2025-11-04T00:00:00"
                 data-date-end="2025-11-11T23:59:59">
                <a href="/sklep/biedronka/gazetka/457728/" class="leaflet__link"></a>
                <div class="leaflet__cover">
                    <img src="https://imgproxy.blix.pl/image/leaflet/457728/cover.jpg" />
                </div>
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflets = scraper._extract_entities(soup, "https://blix.pl/sklep/biedronka/")

        assert len(leaflets) == 2
        assert leaflets[0].leaflet_id == 457727
        assert leaflets[1].leaflet_id == 457728

    def test_extract_entities_no_container(self, mock_driver):
        """Test extracting when no leaflet container found."""
        html = """
        <div>
            <p>No leaflets available</p>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflets = scraper._extract_entities(soup, "https://blix.pl/sklep/biedronka/")

        assert len(leaflets) == 0

    def test_extract_leaflet_complete_data(self, mock_driver):
        """Test extracting leaflet with complete data."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Od środy"
             data-date-start="2025-10-29T00:00:00"
             data-date-end="2025-11-05T23:59:59">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://imgproxy.blix.pl/image/leaflet/457727/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert leaflet.leaflet_id == 457727
        assert leaflet.shop_slug == "biedronka"
        assert leaflet.name == "Od środy"
        assert (
            str(leaflet.cover_image_url)
            == "https://imgproxy.blix.pl/image/leaflet/457727/cover.jpg"
        )
        assert str(leaflet.url) == "https://blix.pl/sklep/biedronka/gazetka/457727/"

    def test_extract_leaflet_active_status(self, mock_driver):
        """Test extracting leaflet with active status."""
        # Use naive datetimes to match scraper behavior
        now = datetime.utcnow()
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)

        html = f"""
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Active Leaflet"
             data-date-start="{start.isoformat()}"
             data-date-end="{end.isoformat()}">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://example.com/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert leaflet.status == LeafletStatus.ACTIVE

    def test_extract_leaflet_upcoming_status(self, mock_driver):
        """Test extracting leaflet with upcoming status."""
        # Use naive datetimes to match scraper behavior
        now = datetime.utcnow()
        start = now + timedelta(days=5)
        end = now + timedelta(days=12)

        html = f"""
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Upcoming Leaflet"
             data-date-start="{start.isoformat()}"
             data-date-end="{end.isoformat()}">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://example.com/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert leaflet.status == LeafletStatus.UPCOMING

    def test_extract_leaflet_archived_status(self, mock_driver):
        """Test extracting leaflet with archived status."""
        # Use naive datetimes to match scraper behavior
        now = datetime.utcnow()
        start = now - timedelta(days=10)
        end = now - timedelta(days=3)

        html = f"""
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Archived Leaflet"
             data-date-start="{start.isoformat()}"
             data-date-end="{end.isoformat()}">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://example.com/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert leaflet.status == LeafletStatus.ARCHIVED

    def test_extract_leaflet_incomplete_data(self, mock_driver):
        """Test extracting leaflet with incomplete data."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Incomplete Leaflet">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is None

    def test_extract_leaflet_missing_link(self, mock_driver):
        """Test extracting leaflet without link."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="No Link Leaflet"
             data-date-start="2025-10-29T00:00:00"
             data-date-end="2025-11-05T23:59:59">
            <div class="leaflet__cover">
                <img src="https://example.com/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is None

    def test_extract_leaflet_missing_cover_image(self, mock_driver):
        """Test extracting leaflet without cover image."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="No Cover Leaflet"
             data-date-start="2025-10-29T00:00:00"
             data-date-end="2025-11-05T23:59:59">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert "placeholder" in str(leaflet.cover_image_url)

    def test_extract_leaflet_relative_url(self, mock_driver):
        """Test extracting leaflet with relative URL."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Relative URL Leaflet"
             data-date-start="2025-10-29T00:00:00"
             data-date-end="2025-11-05T23:59:59">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://example.com/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert str(leaflet.url) == "https://blix.pl/sklep/biedronka/gazetka/457727/"

    def test_extract_leaflet_absolute_url(self, mock_driver):
        """Test extracting leaflet with absolute URL."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Absolute URL Leaflet"
             data-date-start="2025-10-29T00:00:00"
             data-date-end="2025-11-05T23:59:59">
            <a href="https://blix.pl/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://example.com/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert str(leaflet.url) == "https://blix.pl/sklep/biedronka/gazetka/457727/"

    def test_extract_leaflet_data_src_priority(self, mock_driver):
        """Test that data-src is prioritized over src for cover image."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Lazy Load Leaflet"
             data-date-start="2025-10-29T00:00:00"
             data-date-end="2025-11-05T23:59:59">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://blix.pl/fallback.jpg" data-src="https://blix.pl/lazy.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert "lazy.jpg" in str(leaflet.cover_image_url)

    def test_extract_leaflet_invalid_date(self, mock_driver):
        """Test extracting leaflet with invalid date."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="Invalid Date Leaflet"
             data-date-start="invalid-date"
             data-date-end="2025-11-05T23:59:59">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://example.com/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is None

    def test_extract_leaflet_page_count_none(self, mock_driver):
        """Test that page_count is None for leaflets from listing."""
        html = """
        <div class="leaflet section-n__item"
             data-leaflet-id="457727"
             data-leaflet-name="No Page Count"
             data-date-start="2025-10-29T00:00:00"
             data-date-end="2025-11-05T23:59:59">
            <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
            <div class="leaflet__cover">
                <img src="https://example.com/cover.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        leaflet_div = soup.select_one(".leaflet.section-n__item")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflet = scraper._extract_leaflet(leaflet_div)

        assert leaflet is not None
        assert leaflet.page_count is None

    def test_scrape_success(self, mock_driver):
        """Test successful scraping workflow."""
        html = """
        <div class="section-n__items--leaflets">
            <div class="leaflet section-n__item"
                 data-leaflet-id="457727"
                 data-leaflet-name="Test Leaflet"
                 data-date-start="2025-10-29T00:00:00"
                 data-date-end="2025-11-05T23:59:59">
                <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
                <div class="leaflet__cover">
                    <img src="https://example.com/cover.jpg" />
                </div>
            </div>
        </div>
        """

        mock_driver.page_source = html

        with patch("src.webdriver.helpers.human_delay"):
            with patch("src.webdriver.helpers.scroll_to_bottom"):
                scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
                leaflets = scraper.scrape("https://blix.pl/sklep/biedronka/")

        assert len(leaflets) == 1
        assert leaflets[0].name == "Test Leaflet"
        mock_driver.get.assert_called_once_with("https://blix.pl/sklep/biedronka/")

    def test_scrape_error_handling(self, mock_driver):
        """Test error handling during scraping."""
        mock_driver.get.side_effect = Exception("Network error")

        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")

        with pytest.raises(Exception, match="Network error"):
            scraper.scrape("https://blix.pl/sklep/biedronka/")

    def test_extract_entities_handles_exceptions(self, mock_driver):
        """Test that extraction handles individual leaflet errors gracefully."""
        html = """
        <div class="section-n__items--leaflets">
            <div class="leaflet section-n__item"
                 data-leaflet-id="457727"
                 data-leaflet-name="Valid Leaflet"
                 data-date-start="2025-10-29T00:00:00"
                 data-date-end="2025-11-05T23:59:59">
                <a href="/sklep/biedronka/gazetka/457727/" class="leaflet__link"></a>
                <div class="leaflet__cover">
                    <img src="https://example.com/cover1.jpg" />
                </div>
            </div>
            <div class="leaflet section-n__item"
                 data-leaflet-id="457728"
                 data-leaflet-name="Invalid Leaflet"
                 data-date-start="invalid"
                 data-date-end="invalid">
                <a href="/sklep/biedronka/gazetka/457728/" class="leaflet__link"></a>
                <div class="leaflet__cover">
                    <img src="https://example.com/cover2.jpg" />
                </div>
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = LeafletScraper(mock_driver, shop_slug="biedronka")
        leaflets = scraper._extract_entities(soup, "https://blix.pl/sklep/biedronka/")

        # Should extract valid leaflet and skip invalid one
        assert len(leaflets) == 1
        assert leaflets[0].name == "Valid Leaflet"
