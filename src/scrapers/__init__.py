"""Scrapers package."""

from .shop_scraper import ShopScraper
from .leaflet_scraper import LeafletScraper
from .offer_scraper import OfferScraper
from .keyword_scraper import KeywordScraper

__all__ = ["ShopScraper", "LeafletScraper", "OfferScraper", "KeywordScraper"]