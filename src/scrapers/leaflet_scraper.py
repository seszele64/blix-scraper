"""Scraper for leaflet listings."""

from datetime import datetime, timezone
from typing import List, Optional

from bs4 import BeautifulSoup, Tag
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By

from ..domain.entities import Leaflet, LeafletStatus
from ..utils import absolutize_url
from ..webdriver.helpers import wait_for_element
from .base import BaseScraper


class LeafletScraper(BaseScraper[Leaflet]):
    """
    Scraper for leaflet listings.

    Extracts leaflets from shop pages (e.g., https://blix.pl/sklep/biedronka/)
    """

    def __init__(self, driver, shop_slug: str) -> None:  # type: ignore[no-untyped-def]
        """
        Initialize leaflet scraper.

        Args:
            driver: Selenium WebDriver
            shop_slug: Shop slug for this scraper
        """
        super().__init__(driver)
        self.shop_slug = shop_slug

    def _wait_for_content(self) -> None:
        """Wait for leaflet items to load."""
        wait_for_element(self.driver, By.CSS_SELECTOR, ".section-n__items--leaflets", timeout=10)

    def _should_scroll(self) -> bool:
        """Scroll to load all leaflets."""
        return True

    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[Leaflet]:
        """Extract Leaflet entities from HTML."""
        leaflets: List[Leaflet] = []

        # Find leaflet container
        container = soup.select_one(".section-n__items--leaflets")
        if not container:
            self._logger.warning("no_leaflets_container", url=url)
            return leaflets

        # Extract each leaflet
        leaflet_divs = container.select(".leaflet.section-n__item")
        self._logger.info("found_leaflets", count=len(leaflet_divs))

        for leaflet_div in leaflet_divs:
            try:
                leaflet = self._extract_leaflet(leaflet_div)
                if leaflet:
                    leaflets.append(leaflet)
            except Exception as e:
                self._logger.warning(
                    "leaflet_extraction_error", error=str(e), html=str(leaflet_div)[:200]
                )
                continue

        return leaflets

    def _extract_leaflet(self, leaflet_div: Tag) -> Optional[Leaflet]:
        """
        Extract single leaflet from div.

        Args:
            leaflet_div: BeautifulSoup Tag for leaflet div

        Returns:
            Leaflet entity or None if extraction fails
        """
        # Extract from data attributes
        leaflet_id = leaflet_div.get("data-leaflet-id")
        leaflet_name = leaflet_div.get("data-leaflet-name")
        date_start = leaflet_div.get("data-date-start")
        date_end = leaflet_div.get("data-date-end")

        # Get URL from link
        link = leaflet_div.select_one(".leaflet__link")
        if not link:
            self._logger.debug("no_leaflet_link")
            return None

        leaflet_url = link.get("href")

        # Get cover image
        cover_img = leaflet_div.select_one(".leaflet__cover img")
        cover_image_url = None
        if cover_img:
            cover_image_url = cover_img.get("data-src") or cover_img.get("src")

        # Validate required fields
        if not all([leaflet_id, leaflet_name, date_start, date_end, leaflet_url]):
            self._logger.warning(
                "incomplete_leaflet_data",
                leaflet_id=leaflet_id,
                has_name=bool(leaflet_name),
                has_dates=bool(date_start and date_end),
                has_url=bool(leaflet_url),
            )
            return None

        # Parse dates
        try:
            valid_from = date_parser.parse(str(date_start))
            valid_until = date_parser.parse(str(date_end))
        except Exception as e:
            self._logger.error(
                "date_parse_failed",
                leaflet_id=leaflet_id,
                date_start=date_start,
                date_end=date_end,
                error=str(e),
            )
            return None

        # Determine status
        now = datetime.now(timezone.utc)
        if now < valid_from:
            status = LeafletStatus.UPCOMING
        elif now > valid_until:
            status = LeafletStatus.ARCHIVED
        else:
            status = LeafletStatus.ACTIVE

        # Create Leaflet entity
        try:
            # Make sure URL is absolute
            leaflet_url = absolutize_url(leaflet_url) if leaflet_url else None

            # Default cover image if not found
            if not cover_image_url:
                cover_image_url = "https://blix.pl/build/frontend/images/placeholder.png"

            leaflet = Leaflet(
                leaflet_id=int(leaflet_id),
                shop_slug=self.shop_slug,
                name=str(leaflet_name),
                cover_image_url=cover_image_url,
                url=leaflet_url,
                valid_from=valid_from,
                valid_until=valid_until,
                status=status,
                page_count=None,  # Not available in listing
                scraped_at=datetime.now(timezone.utc),
            )

            self._logger.debug(
                "leaflet_extracted", leaflet_id=leaflet_id, name=leaflet.name, status=status
            )
            return leaflet

        except Exception as e:
            self._logger.error(
                "leaflet_creation_failed", leaflet_id=leaflet_id, error=str(e), exc_info=True
            )
            return None
