"""Tests for ShopScraper."""

import pytest
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch

from src.scrapers.shop_scraper import ShopScraper
from src.domain.entities import Shop


class TestShopScraper:
    """Tests for ShopScraper class."""
    
    def test_extract_shop_from_html(self, mock_driver):
        """Test extracting shop from HTML element."""
        html = """
        <a href="/sklep/biedronka/" title="Biedronka">
            <div class="brand section-n__item">
                <img class="brand__logo" data-src="https://img.blix.pl/brand/23.jpg" />
            </div>
        </a>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        brand_div = soup.select_one('.brand')
        
        scraper = ShopScraper(mock_driver)
        shop = scraper._extract_shop(brand_div, is_popular=True)
        
        assert shop is not None
        assert shop.slug == "biedronka"
        assert shop.name == "Biedronka"
        assert shop.is_popular is True
    
    def test_extract_multiple_shops(self, mock_driver):
        """Test extracting multiple shops from page."""
        html = """
        <section>
            <h2>Popularne sklepy</h2>
            <div class="section-n__items--brands">
                <a href="/sklep/biedronka/" title="Biedronka">
                    <div class="brand section-n__item">
                        <img class="brand__logo" data-src="https://img.blix.pl/brand/23.jpg" />
                    </div>
                </a>
                <a href="/sklep/lidl/" title="Lidl">
                    <div class="brand section-n__item">
                        <img class="brand__logo" data-src="https://img.blix.pl/brand/24.jpg" />
                    </div>
                </a>
            </div>
        </section>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        
        scraper = ShopScraper(mock_driver)
        shops = scraper._extract_entities(soup, "https://blix.pl/sklepy/")
        
        assert len(shops) == 2
        assert shops[0].slug == "biedronka"
        assert shops[1].slug == "lidl"
        assert all(s.is_popular for s in shops)
    
    def test_extract_shop_incomplete_data(self, mock_driver):
        """Test handling incomplete shop data."""
        html = """
        <a href="/sklep/biedronka/">
            <div class="brand section-n__item">
                <!-- Missing logo -->
            </div>
        </a>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        brand_div = soup.select_one('.brand')
        
        scraper = ShopScraper(mock_driver)
        shop = scraper._extract_shop(brand_div, is_popular=False)
        
        assert shop is None