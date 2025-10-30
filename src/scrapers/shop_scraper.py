"""Scraper for shop/brand listings."""

from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from selenium.webdriver.common.by import By
from datetime import datetime

from .base import BaseScraper
from ..domain.entities import Shop
from ..webdriver.helpers import wait_for_element


class ShopScraper(BaseScraper[Shop]):
    """
    Scraper for shop/brand listings.
    
    Extracts shops from https://blix.pl/sklepy/
    """
    
    def _wait_for_content(self) -> None:
        """Wait for brand items to load."""
        wait_for_element(
            self.driver,
            By.CSS_SELECTOR,
            '.section-n__items--brands',
            timeout=10
        )
    
    def _should_scroll(self) -> bool:
        """Scroll to load all shops."""
        return True
    
    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[Shop]:
        """Extract Shop entities from HTML."""
        shops: List[Shop] = []
        
        # Find all brand containers
        containers = soup.select('.section-n__items--brands')
        self._logger.info("found_containers", count=len(containers))
        
        for container in containers:
            # Determine if this is "popular shops" section
            section = container.find_parent('section')
            is_popular = False
            if section:
                heading = section.select_one('h2')
                if heading and 'Popularne sklepy' in heading.text:
                    is_popular = True
                    self._logger.debug("found_popular_section")
            
            # Extract each brand
            brand_divs = container.select('.brand.section-n__item')
            self._logger.debug(
                "extracting_brands",
                count=len(brand_divs),
                is_popular=is_popular
            )
            
            for brand_div in brand_divs:
                try:
                    shop = self._extract_shop(brand_div, is_popular)
                    if shop:
                        shops.append(shop)
                except Exception as e:
                    self._logger.warning(
                        "shop_extraction_error",
                        error=str(e),
                        html=str(brand_div)[:200]
                    )
                    continue
        
        return shops
    
    def _extract_shop(self, brand_div: Tag, is_popular: bool) -> Optional[Shop]:
        """
        Extract single shop from brand div.
        
        Args:
            brand_div: BeautifulSoup Tag for brand div
            is_popular: Whether shop is in popular section
            
        Returns:
            Shop entity or None if extraction fails
        """
        # Get parent link
        link = brand_div.find_parent('a')
        if not link:
            self._logger.debug("no_parent_link")
            return None
        
        href = link.get('href', '')
        if not href:
            return None
            
        # Extract slug from URL (e.g., /sklep/biedronka/ -> biedronka)
        slug = href.strip('/').split('/')[-1]
        
        # Extract elements
        name_elem = link.get('title')  # Title attribute has full name
        logo_elem = brand_div.select_one('.brand__logo')
        
        if not all([name_elem, logo_elem, slug]):
            self._logger.warning(
                "incomplete_shop_data",
                slug=slug,
                has_name=bool(name_elem),
                has_logo=bool(logo_elem)
            )
            return None
        
        # Get logo URL (prefer data-src for lazy loaded images)
        logo_url = logo_elem.get('data-src') or logo_elem.get('src')
        if not logo_url:
            self._logger.warning("no_logo_url", slug=slug)
            return None
        
        # Parse leaflet count from nearby text if available
        # This might be in various places depending on the section
        leaflet_count = 0
        # We can enhance this later if needed
        
        # Create Shop entity
        try:
            shop = Shop(
                slug=slug,
                brand_id=None,  # Not available in this view
                name=str(name_elem),
                logo_url=logo_url,
                category=None,  # Could be determined from section heading
                leaflet_count=leaflet_count,
                is_popular=is_popular,
                scraped_at=datetime.utcnow()
            )
            
            self._logger.debug("shop_extracted", slug=slug, name=shop.name)
            return shop
            
        except Exception as e:
            self._logger.error("shop_creation_failed", slug=slug, error=str(e))
            return None