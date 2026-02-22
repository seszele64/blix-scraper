"""Orchestrator for coordinating scraping workflows."""

from typing import List, Optional

import structlog

from .config import settings
from .domain.entities import Keyword, Leaflet, Offer, SearchResult, Shop
from .scrapers.keyword_scraper import KeywordScraper
from .scrapers.leaflet_scraper import LeafletScraper
from .scrapers.offer_scraper import OfferScraper
from .scrapers.search_scraper import SearchScraper
from .scrapers.shop_scraper import ShopScraper
from .storage.field_filter import FieldFilter
from .storage.json_storage import JSONStorage
from .webdriver.driver_factory import DriverFactory

logger = structlog.get_logger(__name__)


class ScraperOrchestrator:
    """
    Orchestrates scraping workflows.

    Coordinates scrapers and storage operations.
    """

    def __init__(self, headless: bool = False):
        """
        Initialize orchestrator.

        Args:
            headless: Run Chrome in headless mode
        """
        self.headless = headless
        self.driver = None

        # Initialize storage
        self.shops_storage = JSONStorage(settings.data_dir / "shops", Shop)
        self.leaflets_storage = JSONStorage(settings.data_dir / "leaflets", Leaflet)

        logger.info("orchestrator_initialized", headless=headless)

    def __enter__(self):
        """Context manager entry - create driver."""
        self.driver = DriverFactory.create_driver(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup driver."""
        if self.driver:
            self.driver.quit()
            logger.info("driver_closed")

    def scrape_all_shops(self) -> List[Shop]:
        """
        Scrape all shops from main page.

        Returns:
            List of scraped Shop entities
        """
        logger.info("scraping_shops_started")

        scraper = ShopScraper(self.driver)
        shops = scraper.scrape(settings.shops_url)

        # Save all shops to single file
        self.shops_storage.save_many(shops, "shops.json")

        # Also save individual shop files
        for shop in shops:
            self.shops_storage.save(shop, f"{shop.slug}.json")

        logger.info("scraping_shops_completed", count=len(shops))
        return shops

    def scrape_shop_leaflets(self, shop_slug: str) -> List[Leaflet]:
        """
        Scrape all leaflets for a specific shop.

        Args:
            shop_slug: Shop slug (e.g., "biedronka")

        Returns:
            List of scraped Leaflet entities
        """
        logger.info("scraping_leaflets_started", shop_slug=shop_slug)

        url = f"{settings.base_url}/sklep/{shop_slug}/"
        scraper = LeafletScraper(self.driver, shop_slug)
        leaflets = scraper.scrape(url)

        # Create shop directory if needed
        shop_dir = settings.data_dir / "leaflets" / shop_slug
        shop_dir.mkdir(parents=True, exist_ok=True)

        # Save each leaflet
        leaflets_storage = JSONStorage(shop_dir, Leaflet)
        for leaflet in leaflets:
            leaflets_storage.save(leaflet, f"{leaflet.leaflet_id}.json")

        logger.info("scraping_leaflets_completed", shop_slug=shop_slug, count=len(leaflets))
        return leaflets

    def scrape_leaflet_offers(
        self, shop_slug: str, leaflet_id: int, field_filter: Optional[FieldFilter] = None
    ) -> List[Offer]:
        """
        Scrape all offers for a specific leaflet.

        Args:
            shop_slug: Shop slug
            leaflet_id: Leaflet ID
            field_filter: Optional filter for saved JSON fields

        Returns:
            List of scraped Offer entities
        """
        logger.info("scraping_offers_started", shop_slug=shop_slug, leaflet_id=leaflet_id)

        url = f"{settings.base_url}/sklep/{shop_slug}/gazetka/{leaflet_id}/"
        scraper = OfferScraper(self.driver, leaflet_id)
        offers = scraper.scrape(url)

        # Save offers with optional field filtering
        offers_storage = JSONStorage(settings.data_dir / "offers", Offer)
        offers_storage.save_many(offers, f"{leaflet_id}_offers.json", field_filter=field_filter)

        logger.info(
            "scraping_offers_completed",
            shop_slug=shop_slug,
            leaflet_id=leaflet_id,
            count=len(offers),
        )
        return offers

    def scrape_leaflet_keywords(self, shop_slug: str, leaflet_id: int) -> List[Keyword]:
        """
        Scrape keywords for a specific leaflet.

        Args:
            shop_slug: Shop slug
            leaflet_id: Leaflet ID

        Returns:
            List of scraped Keyword entities
        """
        logger.info("scraping_keywords_started", shop_slug=shop_slug, leaflet_id=leaflet_id)

        url = f"{settings.base_url}/sklep/{shop_slug}/gazetka/{leaflet_id}/"
        scraper = KeywordScraper(self.driver, leaflet_id)
        keywords = scraper.scrape(url)

        # Save keywords
        keywords_storage = JSONStorage(settings.data_dir / "keywords", Keyword)
        keywords_storage.save_many(keywords, f"{leaflet_id}_keywords.json")

        logger.info(
            "scraping_keywords_completed",
            shop_slug=shop_slug,
            leaflet_id=leaflet_id,
            count=len(keywords),
        )
        return keywords

    def search_products(
        self, query: str, filter_by_name: bool = True, field_filter: Optional[FieldFilter] = None
    ) -> List[SearchResult]:
        """
        Search for products across all shops.

        Args:
            query: Search query string
            filter_by_name: If True, only return products with query in name
            field_filter: Optional filter for saved JSON fields

        Returns:
            List of SearchResult entities
        """
        logger.info("search_started", query=query, filter_by_name=filter_by_name)

        url = f"{settings.base_url}/szukaj/?szukaj={query}"
        scraper = SearchScraper(self.driver, query, filter_by_name=filter_by_name)
        results = scraper.scrape(url)

        # Save results with optional field filtering
        search_storage = JSONStorage(settings.data_dir / "search", SearchResult)
        safe_query = "".join(c for c in query if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_query = safe_query.replace(" ", "_")

        filename = f"{safe_query}_filtered.json" if filter_by_name else f"{safe_query}_all.json"
        search_storage.save_many(results, filename, field_filter=field_filter)

        logger.info("search_completed", query=query, count=len(results))
        return results

    def scrape_full_leaflet(
        self, shop_slug: str, leaflet_id: int
    ) -> tuple[List[Offer], List[Keyword]]:
        """
        Scrape both offers and keywords for a leaflet.

        Args:
            shop_slug: Shop slug
            leaflet_id: Leaflet ID

        Returns:
            Tuple of (offers, keywords)
        """
        logger.info("scraping_full_leaflet_started", shop_slug=shop_slug, leaflet_id=leaflet_id)

        offers = self.scrape_leaflet_offers(shop_slug, leaflet_id)
        keywords = self.scrape_leaflet_keywords(shop_slug, leaflet_id)

        logger.info(
            "scraping_full_leaflet_completed",
            shop_slug=shop_slug,
            leaflet_id=leaflet_id,
            offers_count=len(offers),
            keywords_count=len(keywords),
        )

        return offers, keywords

    def scrape_all_shop_data(self, shop_slug: str, active_only: bool = True) -> dict:
        """
        Scrape all data for a shop: leaflets, offers, keywords.

        Args:
            shop_slug: Shop slug
            active_only: Only scrape active leaflets

        Returns:
            Dictionary with scraping statistics
        """
        logger.info("scraping_all_shop_data_started", shop_slug=shop_slug)

        stats = {
            "shop_slug": shop_slug,
            "leaflets_count": 0,
            "offers_count": 0,
            "keywords_count": 0,
            "errors": [],
        }

        # Get all leaflets
        leaflets = self.scrape_shop_leaflets(shop_slug)
        stats["leaflets_count"] = len(leaflets)

        # Filter to active only if requested
        if active_only:
            leaflets = [leaf for leaf in leaflets if leaf.is_active_now()]
            logger.info("filtering_active_leaflets", count=len(leaflets))

        # Scrape each leaflet
        for leaflet in leaflets:
            try:
                offers, keywords = self.scrape_full_leaflet(shop_slug, leaflet.leaflet_id)
                stats["offers_count"] += len(offers)
                stats["keywords_count"] += len(keywords)

            except Exception as e:
                error_msg = f"Failed to scrape leaflet {leaflet.leaflet_id}: {e}"
                logger.error(
                    "leaflet_scrape_failed",
                    shop_slug=shop_slug,
                    leaflet_id=leaflet.leaflet_id,
                    error=str(e),
                    exc_info=True,
                )
                stats["errors"].append(error_msg)

        logger.info("scraping_all_shop_data_completed", **stats)
        return stats
