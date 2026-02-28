"""Base scraper with template method pattern."""

from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

import structlog
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from ..config import settings
from ..webdriver.helpers import human_delay

T = TypeVar("T")

logger = structlog.get_logger(__name__)


class BaseScraper(ABC, Generic[T]):
    """
    Abstract base scraper using Selenium + BeautifulSoup.

    Template Method pattern for scraping workflow.
    """

    def __init__(self, driver: WebDriver):
        """
        Initialize scraper.

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self._logger = structlog.get_logger(self.__class__.__name__)

    @retry(
        stop=stop_after_attempt(settings.scraping.retry.max_attempts),
        wait=wait_exponential_jitter(
            initial=1,
            exp_base=settings.scraping.retry.backoff_factor,
            max=60,
            jitter=1 if settings.scraping.retry.jitter else 0,
        ),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True,
    )
    def scrape(self, url: str) -> List[T]:
        """
        Template method for scraping workflow.

        Steps:
        1. Navigate to URL
        2. Wait for page load
        3. Get page source
        4. Parse HTML
        5. Extract entities
        6. Validate

        Args:
            url: Target URL to scrape

        Returns:
            List of extracted entities
        """
        self._logger.info("scrape_started", url=url)

        try:
            # Navigate
            self.driver.get(url)
            human_delay()  # Anti-detection

            # Wait for content
            self._wait_for_content()

            # Optional: scroll to load lazy content
            if self._should_scroll():
                self._scroll_page()

            # Get HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, "lxml")

            # Extract entities
            entities = self._extract_entities(soup, url)
            validated = self._validate_entities(entities)

            self._logger.info("scrape_completed", url=url, count=len(validated))
            return validated

        except Exception as e:
            self._logger.error("scrape_failed", url=url, error=str(e), exc_info=True)
            raise

    @abstractmethod
    def _wait_for_content(self) -> None:
        """Wait for page-specific content to load."""
        pass

    @abstractmethod
    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[T]:
        """
        Extract domain entities from parsed HTML.

        Args:
            soup: BeautifulSoup parsed HTML
            url: Source URL

        Returns:
            List of extracted entities
        """
        pass

    def _validate_entities(self, entities: List[T]) -> List[T]:
        """
        Validate entities (default: pass-through).

        Override to add custom validation logic.

        Args:
            entities: Extracted entities

        Returns:
            Validated entities
        """
        return entities

    def _should_scroll(self) -> bool:
        """Whether to scroll page (default: False)."""
        return False

    def _scroll_page(self) -> None:
        """Scroll page to trigger lazy loading."""
        from ..webdriver.helpers import scroll_to_bottom

        self._logger.debug("scrolling_page")
        scroll_to_bottom(self.driver)
