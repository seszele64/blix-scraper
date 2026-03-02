"""Scraper service for orchestrating web scraping operations."""

import structlog
from selenium.webdriver.remote.webdriver import WebDriver

from ..config import settings
from ..domain.date_filter import DateFilterOptions
from ..domain.entities import Keyword, Leaflet, Offer, SearchResult, Shop
from ..scrapers.keyword_scraper import KeywordScraper
from ..scrapers.leaflet_scraper import LeafletScraper
from ..scrapers.offer_scraper import OfferScraper
from ..scrapers.search_scraper import SearchScraper
from ..scrapers.shop_scraper import ShopScraper
from ..webdriver.driver_factory import DriverFactory

logger = structlog.get_logger(__name__)


class ScraperService:
    """Service for orchestrating web scraping operations.

    Provides a high-level interface for scraping shops, leaflets, offers,
    and keywords. Manages WebDriver lifecycle and applies date filtering.

    Example:
        >>> with ScraperService(headless=True) as service:
        ...     shops = service.get_shops()
        ...     leaflets = service.get_leaflets("biedronka")
        ...     offers = service.get_offers("biedronka", leaflets[0])
    """

    def __init__(self, headless: bool = False) -> None:
        """Initialize the scraper service.

        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self._driver: WebDriver | None = None

    def __enter__(self) -> "ScraperService":
        """Initialize WebDriver when entering context.

        Returns:
            Self for context manager

        Raises:
            RuntimeError: If WebDriver creation fails
        """
        try:
            self._driver = DriverFactory.create_driver(headless=self.headless)
            logger.info("scraper_service_started", headless=self.headless)
        except Exception as e:
            logger.error("driver_initialization_failed", error=str(e))
            raise RuntimeError(f"Failed to initialize WebDriver: {e}") from e
        return self

    def __exit__(
        self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object | None
    ) -> None:
        """Cleanup WebDriver when exiting context.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self._driver is not None:
            try:
                self._driver.quit()
                logger.info("scraper_service_stopped")
            except Exception as e:
                logger.warning("driver_cleanup_failed", error=str(e))
            finally:
                self._driver = None

    @property
    def driver(self) -> WebDriver:
        """Get the WebDriver instance.

        Returns:
            Active WebDriver instance

        Raises:
            RuntimeError: If service hasn't been started (use context manager)
        """
        if self._driver is None:
            raise RuntimeError(
                "WebDriver not initialized. Use 'with ScraperService() as service:' "
                "to initialize the driver."
            )
        return self._driver

    def get_shops(self) -> list[Shop]:
        """Fetch all shops from blix.pl.

        Returns:
            List of Shop entities

        Raises:
            RuntimeError: If service hasn't been started
        """
        logger.info("fetching_shops")

        try:
            scraper = ShopScraper(self.driver)
            url = settings.shops_url
            shops = scraper.scrape(url)

            logger.info("shops_fetched", count=len(shops))
            return shops

        except Exception as e:
            logger.error("shops_fetch_failed", error=str(e), exc_info=True)
            raise

    def get_leaflets(
        self, shop_slug: str, date_filter: DateFilterOptions | None = None
    ) -> list[Leaflet]:
        """Fetch leaflets for a specific shop.

        Args:
            shop_slug: Shop identifier (e.g., 'biedronka')
            date_filter: Optional date filter to apply

        Returns:
            List of Leaflet entities

        Raises:
            RuntimeError: If service hasn't been started
        """
        logger.info("fetching_leaflets", shop_slug=shop_slug)

        try:
            scraper = LeafletScraper(self.driver, shop_slug=shop_slug)
            url = f"{settings.base_url}/sklep/{shop_slug}/"
            leaflets = scraper.scrape(url)

            # Apply date filtering if provided
            if date_filter is not None and date_filter.has_date_filter():
                predicate = date_filter.to_predicate()
                leaflets = [leaflet for leaflet in leaflets if predicate(leaflet)]
                logger.info("leaflets_filtered", shop_slug=shop_slug, after_filter=len(leaflets))

            logger.info("leaflets_fetched", shop_slug=shop_slug, count=len(leaflets))
            return leaflets

        except Exception as e:
            logger.error("leaflets_fetch_failed", shop_slug=shop_slug, error=str(e), exc_info=True)
            raise

    def get_offers(self, shop_slug: str, leaflet: Leaflet) -> list[Offer]:
        """Fetch offers from a specific leaflet.

        Args:
            shop_slug: Shop identifier (e.g., 'biedronka')
            leaflet: Leaflet entity to scrape offers from

        Returns:
            List of Offer entities

        Raises:
            RuntimeError: If service hasn't been started
        """
        logger.info("fetching_offers", shop_slug=shop_slug, leaflet_id=leaflet.leaflet_id)

        try:
            scraper = OfferScraper(self.driver, leaflet_id=leaflet.leaflet_id)
            url = str(leaflet.url)
            offers = scraper.scrape(url)

            # Link offers to their parent leaflet for date validation
            for offer in offers:
                offer.leaflet = leaflet

            logger.info(
                "offers_fetched",
                shop_slug=shop_slug,
                leaflet_id=leaflet.leaflet_id,
                count=len(offers),
            )
            return offers

        except Exception as e:
            logger.error(
                "offers_fetch_failed",
                shop_slug=shop_slug,
                leaflet_id=leaflet.leaflet_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def get_keywords(self, shop_slug: str, leaflet: Leaflet) -> list[Keyword]:
        """Fetch keywords from a specific leaflet.

        Args:
            shop_slug: Shop identifier (e.g., 'biedronka')
            leaflet: Leaflet entity to scrape keywords from

        Returns:
            List of Keyword entities

        Raises:
            RuntimeError: If service hasn't been started
        """
        logger.info("fetching_keywords", shop_slug=shop_slug, leaflet_id=leaflet.leaflet_id)

        try:
            scraper = KeywordScraper(self.driver, leaflet_id=leaflet.leaflet_id)
            url = str(leaflet.url)
            keywords = scraper.scrape(url)

            logger.info(
                "keywords_fetched",
                shop_slug=shop_slug,
                leaflet_id=leaflet.leaflet_id,
                count=len(keywords),
            )
            return keywords

        except Exception as e:
            logger.error(
                "keywords_fetch_failed",
                shop_slug=shop_slug,
                leaflet_id=leaflet.leaflet_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def search(
        self,
        query: str,
        filter_by_name: bool = False,
        date_filter: DateFilterOptions | None = None,
    ) -> list[SearchResult]:
        """Search for products across all leaflets.

        Args:
            query: Search query string
            filter_by_name: If True, only return products with query in name
            date_filter: Optional date filter to apply

        Returns:
            List of SearchResult entities

        Raises:
            RuntimeError: If service hasn't been started
        """
        logger.info("searching", query=query, filter_by_name=filter_by_name)

        try:
            scraper = SearchScraper(self.driver, search_query=query, filter_by_name=filter_by_name)
            url = f"{settings.base_url}/szukaj/?szukaj={query}"
            results = scraper.scrape(url)

            # Apply date filtering if provided
            if date_filter is not None and date_filter.has_date_filter():
                predicate = date_filter.to_predicate()
                results = [result for result in results if predicate(result)]
                logger.info("results_filtered", query=query, after_filter=len(results))

            logger.info("search_completed", query=query, count=len(results))
            return results

        except Exception as e:
            logger.error("search_failed", query=query, error=str(e), exc_info=True)
            raise
