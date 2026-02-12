"""Tests for KeywordScraper."""

import pytest
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch

from src.scrapers.keyword_scraper import KeywordScraper
from src.domain.entities import Keyword


@pytest.mark.integration
@pytest.mark.scraping
class TestKeywordScraper:
    """Tests for KeywordScraper class."""

    def test_initialization(self, mock_driver):
        """Test KeywordScraper initialization."""
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)

        assert scraper.driver == mock_driver
        assert scraper.leaflet_id == 457727

    def test_wait_for_content(self, mock_driver):
        """Test waiting for keywords section to load."""
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)

        with patch("src.scrapers.keyword_scraper.wait_for_element"):
            scraper._wait_for_content()

    def test_wait_for_content_no_section(self, mock_driver):
        """Test waiting when keywords section doesn't exist."""
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)

        with patch(
            "src.scrapers.keyword_scraper.wait_for_element", side_effect=Exception("Timeout")
        ):
            # Should not raise, just log debug
            scraper._wait_for_content()

    def test_extract_entities_success(self, mock_driver):
        """Test extracting multiple keywords from HTML."""
        html = """
        <div class="keywords">
            <div class="keywords__wrapper">
                <a href="/produkty/artykuly-spozywcze/mieso/kurczak" class="keyword">Kurczak</a>
                <a href="/produkty/artykuly-spozywcze/mieso/wołowina" class="keyword">Wołowina</a>
                <a href="/produkty/artykuly-spozywcze/nabial/mleko" class="keyword">Mleko</a>
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keywords = scraper._extract_entities(
            soup, "https://blix.pl/sklep/biedronka/gazetka/457727/"
        )

        assert len(keywords) == 3
        assert keywords[0].text == "Kurczak"
        assert keywords[1].text == "Wołowina"
        assert keywords[2].text == "Mleko"

    def test_extract_entities_no_keywords_section(self, mock_driver):
        """Test extracting when no keywords section found."""
        html = """
        <div>
            <p>No keywords available</p>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keywords = scraper._extract_entities(
            soup, "https://blix.pl/sklep/biedronka/gazetka/457727/"
        )

        assert len(keywords) == 0

    def test_extract_entities_no_wrapper(self, mock_driver):
        """Test extracting when keywords wrapper not found."""
        html = """
        <div class="keywords">
            <p>No wrapper</p>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keywords = scraper._extract_entities(
            soup, "https://blix.pl/sklep/biedronka/gazetka/457727/"
        )

        assert len(keywords) == 0

    def test_extract_keyword_complete_data(self, mock_driver):
        """Test extracting keyword with complete data."""
        html = """
        <a href="/produkty/artykuly-spozywcze/mieso/kurczak" class="keyword">Kurczak</a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is not None
        assert keyword.leaflet_id == 457727
        assert keyword.text == "Kurczak"
        assert keyword.url == "/produkty/artykuly-spozywcze/mieso/kurczak"
        assert keyword.category_path == "artykuly-spozywcze/mieso/kurczak"

    def test_extract_keyword_simple_url(self, mock_driver):
        """Test extracting keyword with simple URL."""
        html = """
        <a href="/produkty/mieso" class="keyword">Mięso</a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is not None
        assert keyword.text == "Mięso"
        assert keyword.category_path == "mieso"

    def test_extract_keyword_no_category_path(self, mock_driver):
        """Test extracting keyword without category path."""
        html = """
        <a href="/produkty" class="keyword">Produkty</a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is not None
        assert keyword.text == "Produkty"
        assert keyword.category_path == ""

    def test_extract_keyword_incomplete_data(self, mock_driver):
        """Test extracting keyword with incomplete data."""
        html = """
        <a href="/produkty/mieso" class="keyword"></a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is None

    def test_extract_keyword_missing_url(self, mock_driver):
        """Test extracting keyword without URL."""
        html = """
        <a class="keyword">No URL</a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is None

    def test_extract_keyword_with_whitespace(self, mock_driver):
        """Test extracting keyword with whitespace in text."""
        html = """
        <a href="/produkty/mieso" class="keyword">  Mięso  </a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is not None
        assert keyword.text == "Mięso"

    def test_extract_keyword_special_characters(self, mock_driver):
        """Test extracting keyword with special characters."""
        html = """
        <a href="/produkty/artykuly-spozywcze/nabial/ser-zolty" class="keyword">Ser żółty</a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is not None
        assert keyword.text == "Ser żółty"
        assert "ser-zolty" in keyword.category_path

    def test_extract_keyword_deep_category_path(self, mock_driver):
        """Test extracting keyword with deep category path."""
        html = """
        <a href="/produkty/artykuly-spozywcze/mieso/drób/kurczak/udka" class="keyword">Udka z kurczaka</a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is not None
        assert keyword.category_path == "artykuly-spozywcze/mieso/drób/kurczak/udka"

    def test_extract_keyword_absolute_url(self, mock_driver):
        """Test extracting keyword with absolute URL."""
        html = """
        <a href="https://blix.pl/produkty/mieso" class="keyword">Mięso</a>
        """

        soup = BeautifulSoup(html, "lxml")
        keyword_link = soup.select_one("a.keyword")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword = scraper._extract_keyword(keyword_link)

        assert keyword is not None
        assert keyword.url == "https://blix.pl/produkty/mieso"
        # Absolute URLs get full path extracted (includes leading slash)
        assert keyword.category_path == "/blix.pl/produkty/mieso"

    def test_extract_entities_empty_wrapper(self, mock_driver):
        """Test extracting when wrapper has no keywords."""
        html = """
        <div class="keywords">
            <div class="keywords__wrapper">
                <p>No keywords here</p>
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keywords = scraper._extract_entities(
            soup, "https://blix.pl/sklep/biedronka/gazetka/457727/"
        )

        assert len(keywords) == 0

    def test_scrape_success(self, mock_driver):
        """Test successful scraping workflow."""
        html = """
        <div class="keywords">
            <div class="keywords__wrapper">
                <a href="/produkty/mieso" class="keyword">Mięso</a>
                <a href="/produkty/nabial" class="keyword">Nabiał</a>
            </div>
        </div>
        """

        mock_driver.page_source = html

        with patch("src.webdriver.helpers.human_delay"):
            scraper = KeywordScraper(mock_driver, leaflet_id=457727)
            keywords = scraper.scrape("https://blix.pl/sklep/biedronka/gazetka/457727/")

        assert len(keywords) == 2
        assert keywords[0].text == "Mięso"
        assert keywords[1].text == "Nabiał"
        mock_driver.get.assert_called_once_with("https://blix.pl/sklep/biedronka/gazetka/457727/")

    def test_scrape_error_handling(self, mock_driver):
        """Test error handling during scraping."""
        mock_driver.get.side_effect = Exception("Network error")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)

        with pytest.raises(Exception, match="Network error"):
            scraper.scrape("https://blix.pl/sklep/biedronka/gazetka/457727/")

    def test_extract_entities_handles_exceptions(self, mock_driver):
        """Test that extraction handles individual keyword errors gracefully."""
        html = """
        <div class="keywords">
            <div class="keywords__wrapper">
                <a href="/produkty/mieso" class="keyword">Mięso</a>
                <a class="keyword"></a>
                <a href="/produkty/nabial" class="keyword">Nabiał</a>
            </div>
        </div>
        """

        soup = BeautifulSoup(html, "lxml")
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keywords = scraper._extract_entities(
            soup, "https://blix.pl/sklep/biedronka/gazetka/457727/"
        )

        # Should extract valid keywords and skip invalid one
        assert len(keywords) == 2
        assert keywords[0].text == "Mięso"
        assert keywords[1].text == "Nabiał"

    def test_should_scroll_default(self, mock_driver):
        """Test that keyword scraper doesn't scroll by default."""
        scraper = KeywordScraper(mock_driver, leaflet_id=457727)

        assert scraper._should_scroll() is False

    def test_keyword_hash_and_equality(self, mock_driver):
        """Test Keyword hash and equality methods."""
        html1 = """
        <a href="/produkty/mieso" class="keyword">Mięso</a>
        """
        html2 = """
        <a href="/produkty/nabial" class="keyword">Mięso</a>
        """

        soup1 = BeautifulSoup(html1, "lxml")
        soup2 = BeautifulSoup(html2, "lxml")

        scraper = KeywordScraper(mock_driver, leaflet_id=457727)
        keyword1 = scraper._extract_keyword(soup1.select_one("a.keyword"))
        keyword2 = scraper._extract_keyword(soup2.select_one("a.keyword"))

        assert keyword1 is not None
        assert keyword2 is not None
        assert keyword1 == keyword2  # Same text
        assert hash(keyword1) == hash(keyword2)
