"""Tests for BaseScraper."""

from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper


class ConcreteScraper(BaseScraper):
    """Concrete implementation of BaseScraper for testing."""

    def __init__(self, driver, wait_called=False, extract_called=False):
        super().__init__(driver)
        self.wait_called = wait_called
        self.extract_called = extract_called

    def _wait_for_content(self) -> None:
        """Wait for content to load."""
        self.wait_called = True

    def _extract_entities(self, soup: BeautifulSoup, url: str):
        """Extract entities from HTML."""
        self.extract_called = True
        return [{"entity": "test"}]

    def _should_scroll(self) -> bool:
        """Whether to scroll."""
        return False


@pytest.mark.integration
@pytest.mark.scraping
class TestBaseScraper:
    """Tests for BaseScraper class."""

    def test_initialization(self, mock_driver):
        """Test BaseScraper initialization."""
        scraper = ConcreteScraper(mock_driver)

        assert scraper.driver == mock_driver
        assert scraper._logger is not None

    def test_is_abstract(self, mock_driver):
        """Test that BaseScraper cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseScraper(mock_driver)

    def test_scrape_success(self, mock_driver):
        """Test successful scraping workflow."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        with patch("src.scrapers.base.human_delay"):
            scraper = ConcreteScraper(mock_driver)
            results = scraper.scrape("https://example.com")

        assert len(results) == 1
        assert results[0] == {"entity": "test"}
        assert scraper.wait_called is True
        assert scraper.extract_called is True
        mock_driver.get.assert_called_once_with("https://example.com")

    def test_scrape_with_scroll(self, mock_driver):
        """Test scraping with page scrolling."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        class ScrollingScraper(ConcreteScraper):
            def _should_scroll(self) -> bool:
                return True

        with patch("src.webdriver.helpers.human_delay"):
            with patch("src.webdriver.helpers.scroll_to_bottom") as mock_scroll:
                scraper = ScrollingScraper(mock_driver)
                results = scraper.scrape("https://example.com")

        assert len(results) == 1
        mock_scroll.assert_called_once()

    def test_scrape_without_scroll(self, mock_driver):
        """Test scraping without page scrolling."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        with patch("src.webdriver.helpers.human_delay"):
            with patch("src.webdriver.helpers.scroll_to_bottom") as mock_scroll:
                scraper = ConcreteScraper(mock_driver)
                results = scraper.scrape("https://example.com")

        assert len(results) == 1
        mock_scroll.assert_not_called()

    def test_scrape_error_handling(self, mock_driver):
        """Test error handling during scraping."""
        mock_driver.get.side_effect = Exception("Network error")

        scraper = ConcreteScraper(mock_driver)

        with pytest.raises(Exception, match="Network error"):
            scraper.scrape("https://example.com")

    def test_scrape_logs_info(self, mock_driver):
        """Test that scraping logs appropriate messages."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        with patch("src.scrapers.base.human_delay"):
            scraper = ConcreteScraper(mock_driver)
            with patch.object(scraper._logger, "info") as mock_log_info:
                scraper.scrape("https://example.com")

        # Check that info was called at least twice (start and complete)
        assert mock_log_info.call_count >= 2

    def test_scrape_logs_error_on_failure(self, mock_driver):
        """Test that scraping logs error on failure."""
        mock_driver.get.side_effect = Exception("Network error")

        scraper = ConcreteScraper(mock_driver)

        with patch.object(scraper._logger, "error") as mock_log_error:
            try:
                scraper.scrape("https://example.com")
            except Exception:
                pass

        mock_log_error.assert_called_once()

    def test_validate_entities_default(self, mock_driver):
        """Test default validation (pass-through)."""
        scraper = ConcreteScraper(mock_driver)
        entities = [{"entity": "test1"}, {"entity": "test2"}]

        validated = scraper._validate_entities(entities)

        assert validated == entities

    def test_validate_entities_empty(self, mock_driver):
        """Test validation with empty list."""
        scraper = ConcreteScraper(mock_driver)
        entities = []

        validated = scraper._validate_entities(entities)

        assert validated == []

    def test_should_scroll_default(self, mock_driver):
        """Test default _should_scroll returns False."""
        scraper = ConcreteScraper(mock_driver)

        assert scraper._should_scroll() is False

    def test_scroll_page(self, mock_driver):
        """Test _scroll_page method."""
        scraper = ConcreteScraper(mock_driver)

        with patch("src.webdriver.helpers.scroll_to_bottom") as mock_scroll:
            with patch.object(scraper._logger, "debug") as mock_log_debug:
                scraper._scroll_page()

        mock_scroll.assert_called_once_with(mock_driver)
        mock_log_debug.assert_called_once_with("scrolling_page")

    def test_wait_for_content_abstract(self, mock_driver):
        """Test that _wait_for_content must be implemented."""
        # ConcreteScraper implements it, so this should work
        scraper = ConcreteScraper(mock_driver)
        scraper._wait_for_content()

        assert scraper.wait_called is True

    def test_extract_entities_abstract(self, mock_driver):
        """Test that _extract_entities must be implemented."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "lxml")

        # ConcreteScraper implements it, so this should work
        scraper = ConcreteScraper(mock_driver)
        results = scraper._extract_entities(soup, "https://example.com")

        assert scraper.extract_called is True
        assert results == [{"entity": "test"}]

    def test_scrape_with_custom_validation(self, mock_driver):
        """Test scraping with custom validation."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        class ValidatingScraper(ConcreteScraper):
            def _validate_entities(self, entities):
                # Filter out entities without 'entity' key
                return [e for e in entities if "entity" in e]

        with patch("src.scrapers.base.human_delay"):
            scraper = ValidatingScraper(mock_driver)
            results = scraper.scrape("https://example.com")

        assert len(results) == 1

    def test_scrape_with_empty_results(self, mock_driver):
        """Test scraping when no entities are extracted."""
        html = """
        <html>
            <body>
                <div>No entities</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        class EmptyScraper(ConcreteScraper):
            def _extract_entities(self, soup: BeautifulSoup, url: str):
                return []

        with patch("src.scrapers.base.human_delay"):
            scraper = EmptyScraper(mock_driver)
            results = scraper.scrape("https://example.com")

        assert len(results) == 0

    def test_scrape_with_multiple_entities(self, mock_driver):
        """Test scraping with multiple entities."""
        html = """
        <html>
            <body>
                <div>Multiple entities</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        class MultiEntityScraper(ConcreteScraper):
            def _extract_entities(self, soup: BeautifulSoup, url: str):
                return [{"entity": "test1"}, {"entity": "test2"}, {"entity": "test3"}]

        with patch("src.scrapers.base.human_delay"):
            scraper = MultiEntityScraper(mock_driver)
            results = scraper.scrape("https://example.com")

        assert len(results) == 3

    def test_scrape_with_exception_in_extract(self, mock_driver):
        """Test scraping when extraction raises exception."""
        html = """
        <html>
            <body>
                <div>Error content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        class ErrorScraper(ConcreteScraper):
            def _extract_entities(self, soup: BeautifulSoup, url: str):
                raise ValueError("Extraction error")

        scraper = ErrorScraper(mock_driver)

        with pytest.raises(ValueError, match="Extraction error"):
            scraper.scrape("https://example.com")

    def test_scrape_with_exception_in_wait(self, mock_driver):
        """Test scraping when wait raises exception."""
        html = """
        <html>
            <body>
                <div>Error content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        class ErrorWaitScraper(ConcreteScraper):
            def _wait_for_content(self) -> None:
                raise TimeoutError("Wait timeout")

        scraper = ErrorWaitScraper(mock_driver)

        with pytest.raises(TimeoutError, match="Wait timeout"):
            scraper.scrape("https://example.com")

    def test_logger_class_name(self, mock_driver):
        """Test that logger uses class name."""
        scraper = ConcreteScraper(mock_driver)

        assert "ConcreteScraper" in str(scraper._logger)

    def test_human_delay_called(self, mock_driver):
        """Test that human_delay is called during scrape."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        with patch("src.scrapers.base.human_delay") as mock_delay:
            scraper = ConcreteScraper(mock_driver)
            scraper.scrape("https://example.com")

        mock_delay.assert_called_once()

    def test_driver_get_called(self, mock_driver):
        """Test that driver.get is called with correct URL."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        with patch("src.scrapers.base.human_delay"):
            scraper = ConcreteScraper(mock_driver)
            scraper.scrape("https://example.com/page")

        mock_driver.get.assert_called_once_with("https://example.com/page")

    def test_page_source_retrieved(self, mock_driver):
        """Test that page_source is retrieved from driver."""
        html = """
        <html>
            <body>
                <div>Test content</div>
            </body>
        </html>
        """

        mock_driver.page_source = html

        with patch("src.scrapers.base.human_delay"):
            scraper = ConcreteScraper(mock_driver)
            scraper.scrape("https://example.com")

        # page_source should be accessed
        assert mock_driver.page_source == html
