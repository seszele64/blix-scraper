"""Scraper for keywords/tags in leaflets."""

from datetime import datetime, timezone
from typing import List, Optional

from bs4 import BeautifulSoup, Tag
from selenium.webdriver.common.by import By

from ..domain.entities import Keyword
from ..webdriver.helpers import wait_for_element
from .base import BaseScraper


class KeywordScraper(BaseScraper[Keyword]):
    """
    Scraper for keywords/tags in leaflets.

    Extracts keywords from leaflet pages.
    """

    def __init__(self, driver, leaflet_id: int) -> None:  # type: ignore[no-untyped-def]
        """
        Initialize keyword scraper.

        Args:
            driver: Selenium WebDriver
            leaflet_id: Leaflet ID for this scraper
        """
        super().__init__(driver)
        self.leaflet_id = leaflet_id

    def _wait_for_content(self) -> None:
        """Wait for keywords section to load."""
        try:
            wait_for_element(self.driver, By.CSS_SELECTOR, ".keywords", timeout=5)
        except Exception:
            # Keywords section might not exist for all leaflets
            self._logger.debug("no_keywords_section")

    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[Keyword]:
        """Extract Keyword entities from HTML."""
        keywords: List[Keyword] = []

        # Find keywords container
        keywords_div = soup.select_one(".keywords")
        if not keywords_div:
            self._logger.info("no_keywords_found", url=url)
            return keywords

        # Find keyword wrapper
        wrapper = keywords_div.select_one(".keywords__wrapper")
        if not wrapper:
            self._logger.warning("no_keywords_wrapper")
            return keywords

        # Extract each keyword
        keyword_links = wrapper.select("a.keyword")
        self._logger.info("found_keywords", count=len(keyword_links))

        for keyword_link in keyword_links:
            try:
                keyword = self._extract_keyword(keyword_link)
                if keyword:
                    keywords.append(keyword)
            except Exception as e:
                self._logger.warning(
                    "keyword_extraction_error", error=str(e), html=str(keyword_link)[:100]
                )
                continue

        return keywords

    def _extract_keyword(self, keyword_link: Tag) -> Optional[Keyword]:
        """
        Extract single keyword from link.

        Args:
            keyword_link: BeautifulSoup Tag for keyword link

        Returns:
            Keyword entity or None if extraction fails
        """
        text = keyword_link.get_text(strip=True)
        url = keyword_link.get("href")

        if not text or not url:
            self._logger.debug("incomplete_keyword", text=text, url=url)
            return None

        # Parse category path from URL
        # e.g., /produkty/artykuly-spozywcze/mieso/kurczak -> artykuly-spozywcze/mieso/kurczak
        category_path = ""
        if url:
            parts = url.strip("/").split("/")
            if len(parts) > 1:
                category_path = "/".join(parts[1:])  # Skip 'produkty'

        # Create Keyword entity
        try:
            keyword = Keyword(
                leaflet_id=self.leaflet_id,
                text=text,
                url=url,
                category_path=category_path,
                scraped_at=datetime.now(timezone.utc),
            )

            self._logger.debug("keyword_extracted", text=text, category=category_path)
            return keyword

        except Exception as e:
            self._logger.error("keyword_creation_failed", text=text, error=str(e))
            return None
