"""Scraper for product offers within leaflets."""

from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from selenium.webdriver.common.by import By
from datetime import datetime
from dateutil import parser as date_parser
from decimal import Decimal, InvalidOperation

from .base import BaseScraper
from ..domain.entities import Offer
from ..webdriver.helpers import wait_for_element


class OfferScraper(BaseScraper[Offer]):
    """
    Scraper for product offers within leaflets.
    
    Extracts offers from leaflet pages (e.g., https://blix.pl/sklep/biedronka/gazetka/457262/)
    """
    
    def __init__(self, driver, leaflet_id: int):
        """
        Initialize offer scraper.
        
        Args:
            driver: Selenium WebDriver
            leaflet_id: Leaflet ID for this scraper
        """
        super().__init__(driver)
        self.leaflet_id = leaflet_id
    
    def _wait_for_content(self) -> None:
        """Wait for offer items to load."""
        wait_for_element(
            self.driver,
            By.CSS_SELECTOR,
            '.offer.section-n__item',
            timeout=15
        )
    
    def _should_scroll(self) -> bool:
        """Scroll to load all offers."""
        return True
    
    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[Offer]:
        """Extract Offer entities from HTML."""
        offers: List[Offer] = []
        
        # Find all offer divs
        offer_divs = soup.select('.offer.section-n__item')
        self._logger.info("found_offers", count=len(offer_divs))
        
        for offer_div in offer_divs:
            try:
                offer = self._extract_offer(offer_div)
                if offer:
                    offers.append(offer)
            except Exception as e:
                self._logger.warning(
                    "offer_extraction_error",
                    error=str(e),
                    html=str(offer_div)[:200]
                )
                continue
        
        return offers
    
    def _extract_offer(self, offer_div: Tag) -> Optional[Offer]:
        """
        Extract single offer from div.
        
        Args:
            offer_div: BeautifulSoup Tag for offer div
            
        Returns:
            Offer entity or None if extraction fails
        """
        # Extract from data attributes
        name = offer_div.get('data-name')
        price_str = offer_div.get('data-price')
        page_number = offer_div.get('data-page-number')
        date_start = offer_div.get('data-date-start')
        date_end = offer_div.get('data-date-end')
        
        # Position data
        position_x = offer_div.get('data-topleftcorner-x')
        position_y = offer_div.get('data-topleftcorner-y')
        bottom_right_x = offer_div.get('data-bottomrightcorner-x')
        bottom_right_y = offer_div.get('data-bottomrightcorner-y')
        
        # Get image
        img = offer_div.select_one('.offer__img')
        image_url = None
        if img:
            image_url = img.get('data-src') or img.get('src')
        
        # Validate required fields
        if not all([name, page_number, date_start, date_end, image_url]):
            self._logger.warning(
                "incomplete_offer_data",
                name=name,
                has_page=bool(page_number),
                has_dates=bool(date_start and date_end),
                has_image=bool(image_url)
            )
            return None
        
        # Parse price (optional field)
        price: Optional[Decimal] = None
        if price_str and price_str.strip():
            try:
                # Remove currency symbols and whitespace
                price_clean = price_str.strip().replace('zł', '').replace(',', '.').strip()
                if price_clean:
                    price = Decimal(price_clean)
            except (InvalidOperation, ValueError) as e:
                self._logger.debug("price_parse_failed", price_str=price_str, error=str(e))
        
        # Parse dates
        try:
            valid_from = date_parser.parse(str(date_start))
            valid_until = date_parser.parse(str(date_end))
        except Exception as e:
            self._logger.error(
                "date_parse_failed",
                name=name,
                date_start=date_start,
                date_end=date_end,
                error=str(e)
            )
            return None
        
        # Parse position data
        try:
            pos_x = float(position_x) if position_x else 0.0
            pos_y = float(position_y) if position_y else 0.0
            br_x = float(bottom_right_x) if bottom_right_x else 1.0
            br_y = float(bottom_right_y) if bottom_right_y else 1.0
            
            # Calculate width and height
            width = br_x - pos_x
            height = br_y - pos_y
            
        except (ValueError, TypeError) as e:
            self._logger.debug("position_parse_failed", error=str(e))
            pos_x, pos_y, width, height = 0.0, 0.0, 1.0, 1.0
        
        # Create Offer entity
        try:
            # Ensure image URL is absolute
            if image_url and not image_url.startswith('http'):
                image_url = f"https://blix.pl{image_url}"
            
            offer = Offer(
                leaflet_id=self.leaflet_id,
                name=str(name),
                price=price,
                image_url=image_url,
                page_number=int(page_number),
                position_x=pos_x,
                position_y=pos_y,
                width=width,
                height=height,
                valid_from=valid_from,
                valid_until=valid_until,
                scraped_at=datetime.utcnow()
            )
            
            self._logger.debug("offer_extracted", name=name, price=price)
            return offer
            
        except Exception as e:
            self._logger.error(
                "offer_creation_failed",
                name=name,
                error=str(e),
                exc_info=True
            )
            return None