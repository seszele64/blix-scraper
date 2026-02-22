"""Tests for OfferScraper."""

from decimal import Decimal
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.scrapers.offer_scraper import OfferScraper


@pytest.mark.integration
@pytest.mark.scraping
class TestOfferScraper:
    """Tests for OfferScraper class."""

    def test_initialization(self, mock_driver):
        """Test OfferScraper initialization."""
        scraper = OfferScraper(mock_driver, leaflet_id=457727)

        assert scraper.driver == mock_driver
        assert scraper.leaflet_id == 457727

    def test_wait_for_content(self, mock_driver):
        """Test waiting for offer items to load."""
        scraper = OfferScraper(mock_driver, leaflet_id=457727)

        with patch("src.scrapers.offer_scraper.wait_for_element"):
            scraper._wait_for_content()

    def test_should_scroll(self, mock_driver):
        """Test that offer scraper should scroll."""
        scraper = OfferScraper(mock_driver, leaflet_id=457727)

        assert scraper._should_scroll() is True

    def test_extract_entities_success(self, mock_driver):
        """Test extracting multiple offers from HTML."""
        html = """
        <div class="section-n__items--leaflets">
            <div class="offer section-n__item"
                 data-name="Chleb żytni 500g"
                 data-price="4,99 zł"
                 data-page-number="1"
                 data-date-start="2025-10-29T00:00:00Z"
                 data-date-end="2025-11-05T23:59:59Z"
                 data-topleftcorner-x="0.1"
                 data-topleftcorner-y="0.2"
                 data-bottomrightcorner-x="0.5"
                 data-bottomrightcorner-y="0.6">
                <img class="offer__img" data-src="https://example.com/image1.jpg" />
            </div>
            <div class="offer section-n__item"
                 data-name="Mleko UHT 1l"
                 data-price="3,49 zł"
                 data-page-number="2"
                 data-date-start="2025-10-29T00:00:00Z"
                 data-date-end="2025-11-05T23:59:59Z"
                 data-topleftcorner-x="0.6"
                 data-topleftcorner-y="0.1"
                 data-bottomrightcorner-x="0.9"
                 data-bottomrightcorner-y="0.5">
                <img class="offer__img" src="https://example.com/image2.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offers = scraper._extract_entities(soup, "https://blix.pl/sklep/biedronka/gazetka/457727/")

        assert len(offers) == 2
        assert offers[0].name == "Chleb żytni 500g"
        assert offers[1].name == "Mleko UHT 1l"

    def test_extract_entities_no_offers(self, mock_driver):
        """Test extracting when no offers found."""
        html = """
        <div class="section-n__items--leaflets">
            <div>No offers available</div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offers = scraper._extract_entities(soup, "https://blix.pl/sklep/biedronka/gazetka/457727/")

        assert len(offers) == 0

    def test_extract_offer_complete_data(self, mock_driver):
        """Test extracting offer with complete data."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z"
             data-topleftcorner-x="0.1"
             data-topleftcorner-y="0.2"
             data-bottomrightcorner-x="0.5"
             data-bottomrightcorner-y="0.6">
            <img class="offer__img" data-src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert offer.leaflet_id == 457727
        assert offer.name == "Chleb żytni 500g"
        assert offer.price == Decimal("4.99")
        assert offer.page_number == 1
        assert offer.position_x == 0.1
        assert offer.position_y == 0.2
        assert offer.width == pytest.approx(0.4)
        assert offer.height == pytest.approx(0.4)
        assert str(offer.image_url) == "https://example.com/image.jpg"

    def test_extract_offer_without_price(self, mock_driver):
        """Test extracting offer without price."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert offer.price is None

    def test_extract_offer_with_invalid_price(self, mock_driver):
        """Test extracting offer with invalid price."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="invalid"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert offer.price is None

    def test_extract_offer_without_position(self, mock_driver):
        """Test extracting offer without position data."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert offer.position_x == 0.0
        assert offer.position_y == 0.0
        assert offer.width == 1.0
        assert offer.height == 1.0

    def test_extract_offer_incomplete_data(self, mock_driver):
        """Test extracting offer with incomplete data."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is None

    def test_extract_offer_missing_image(self, mock_driver):
        """Test extracting offer without image."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is None

    def test_extract_offer_invalid_date(self, mock_driver):
        """Test extracting offer with invalid date."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł"
             data-page-number="1"
             data-date-start="invalid-date"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is None

    def test_extract_offer_relative_image_url(self, mock_driver):
        """Test extracting offer with relative image URL."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="/image/product.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert str(offer.image_url) == "https://blix.pl/image/product.jpg"

    def test_extract_offer_data_src_priority(self, mock_driver):
        """Test that data-src is prioritized over src."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="/fallback.jpg" data-src="/lazy.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert "lazy.jpg" in str(offer.image_url)

    def test_extract_offer_price_with_currency(self, mock_driver):
        """Test extracting offer price with currency symbol."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert offer.price == Decimal("4.99")

    def test_extract_offer_price_with_comma(self, mock_driver):
        """Test extracting offer price with comma decimal separator."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="12,50 zł"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert offer.price == Decimal("12.50")

    def test_extract_offer_price_whitespace(self, mock_driver):
        """Test extracting offer price with whitespace."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="  4,99 zł  "
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert offer.price == Decimal("4.99")

    def test_extract_offer_position_calculation(self, mock_driver):
        """Test correct position calculation."""
        html = """
        <div class="offer section-n__item"
             data-name="Chleb żytni 500g"
             data-price="4,99 zł"
             data-page-number="1"
             data-date-start="2025-10-29T00:00:00Z"
             data-date-end="2025-11-05T23:59:59Z"
             data-topleftcorner-x="0.2"
             data-topleftcorner-y="0.3"
             data-bottomrightcorner-x="0.7"
             data-bottomrightcorner-y="0.8">
            <img class="offer__img" src="https://example.com/image.jpg" />
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        offer_div = soup.select_one(".offer.section-n__item")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offer = scraper._extract_offer(offer_div)

        assert offer is not None
        assert offer.position_x == 0.2
        assert offer.position_y == 0.3
        assert offer.width == pytest.approx(0.5)  # 0.7 - 0.2
        assert offer.height == 0.5  # 0.8 - 0.3

    def test_scrape_success(self, mock_driver):
        """Test successful scraping workflow."""
        html = """
        <div class="section-n__items--leaflets">
            <div class="offer section-n__item"
                 data-name="Chleb żytni 500g"
                 data-price="4,99 zł"
                 data-page-number="1"
                 data-date-start="2025-10-29T00:00:00Z"
                 data-date-end="2025-11-05T23:59:59Z">
                <img class="offer__img" src="https://example.com/image.jpg" />
            </div>
        </div>
        """

        mock_driver.page_source = html

        with patch("src.webdriver.helpers.human_delay"):
            with patch("src.webdriver.helpers.scroll_to_bottom"):
                scraper = OfferScraper(mock_driver, leaflet_id=457727)
                offers = scraper.scrape("https://blix.pl/sklep/biedronka/gazetka/457727/")

        assert len(offers) == 1
        assert offers[0].name == "Chleb żytni 500g"
        mock_driver.get.assert_called_once_with("https://blix.pl/sklep/biedronka/gazetka/457727/")

    def test_scrape_error_handling(self, mock_driver):
        """Test error handling during scraping."""
        mock_driver.get.side_effect = Exception("Network error")

        scraper = OfferScraper(mock_driver, leaflet_id=457727)

        with pytest.raises(Exception, match="Network error"):
            scraper.scrape("https://blix.pl/sklep/biedronka/gazetka/457727/")

    def test_extract_entities_handles_exceptions(self, mock_driver):
        """Test that extraction handles individual offer errors gracefully."""
        html = """
        <div class="section-n__items--leaflets">
            <div class="offer section-n__item"
                 data-name="Valid Offer"
                 data-price="4,99 zł"
                 data-page-number="1"
                 data-date-start="2025-10-29T00:00:00Z"
                 data-date-end="2025-11-05T23:59:59Z">
                <img class="offer__img" src="https://example.com/image1.jpg" />
            </div>
            <div class="offer section-n__item"
                 data-name="Invalid Offer"
                 data-price="invalid"
                 data-page-number="invalid"
                 data-date-start="invalid"
                 data-date-end="invalid">
                <img class="offer__img" src="https://example.com/image2.jpg" />
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = OfferScraper(mock_driver, leaflet_id=457727)
        offers = scraper._extract_entities(soup, "https://blix.pl/sklep/biedronka/gazetka/457727/")

        # Should extract valid offer and skip invalid one
        assert len(offers) == 1
        assert offers[0].name == "Valid Offer"
