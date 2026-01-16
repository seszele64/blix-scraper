---
title: API Reference
description: Complete API documentation for blix-scraper
category: documentation
tags:
  - api-reference
  - documentation
  - modules
  - functions
created: 2026-01-16
updated: 2026-01-16
---

# API Reference

Complete documentation for the blix-scraper public API.

## Table of Contents

1. [Modules](#modules)
2. [CLI Module](#cli-module)
3. [Config Module](#config-module)
4. [Domain Entities](#domain-entities)
5. [Orchestrator](#orchestrator)
6. [Scrapers](#scrapers)
7. [Storage](#storage)
8. [WebDriver](#webdriver)

---

## Modules

### src

Main package module.

```python
from src import main
```

---

## CLI Module

### src.cli

CLI interface module using Typer.

**Commands**:
- `scrape-shops` - Scrape all shops
- `scrape-leaflets` - Scrape leaflets for a shop
- `scrape-offers` - Scrape offers for a leaflet
- `scrape-full-shop` - Scrape all data for a shop
- `search` - Search for products
- `list-shops` - List scraped shops
- `list-leaflets` - List leaflets for a shop
- `config` - Show current configuration

**Usage**:
```bash
python -m src.cli <command> [arguments] [options]
```

### Functions

#### scrape_shops

```python
def scrape_shops(headless: bool = False) -> List[Shop]:
    """
    Scrape all shops from blix.pl.

    Args:
        headless: Run browser in headless mode

    Returns:
        List of Shop entities

    Example:
        >>> from src.cli import scrape_shops
        >>> shops = scrape_shops(headless=True)
        >>> len(shops)
        50
    """
```

#### search

```python
def search(
    query: str,
    headless: bool = False,
    show_all: bool = False,
    no_filter: bool = False
) -> List[SearchResult]:
    """
    Search for products across all shops.

    Args:
        query: Search query string
        headless: Run browser in headless mode
        show_all: Show all results (default: limit to 20)
        no_filter: Don't filter by product name

    Returns:
        List of SearchResult entities

    Example:
        >>> from src.cli import search
        >>> results = search("kawa", show_all=True)
        >>> len(results)
        100
    """
```

#### scrape_leaflets

```python
def scrape_leaflets(shop: str, headless: bool = False) -> List[Leaflet]:
    """
    Scrape all leaflets for a specific shop.

    Args:
        shop: Shop slug (e.g., 'biedronka')
        headless: Run browser in headless mode

    Returns:
        List of Leaflet entities

    Example:
        >>> from src.cli import scrape_leaflets
        >>> leaflets = scrape_leaflets("biedronka")
        >>> len(leaflets)
        13
    """
```

#### scrape_offers

```python
def scrape_offers(
    shop: str,
    leaflet_id: int,
    headless: bool = False
) -> List[Offer]:
    """
    Scrape offers for a specific leaflet.

    Args:
        shop: Shop slug
        leaflet_id: Leaflet ID
        headless: Run browser in headless mode

    Returns:
        List of Offer entities

    Example:
        >>> from src.cli import scrape_offers
        >>> offers = scrape_offers("biedronka", 457727)
        >>> len(offers)
        50
    """
```

#### scrape_full_shop

```python
def scrape_full_shop(
    shop: str,
    active_only: bool = True,
    headless: bool = False
) -> dict:
    """
    Scrape all data for a shop.

    Args:
        shop: Shop slug
        active_only: Only scrape active leaflets
        headless: Run browser in headless mode

    Returns:
        Dictionary with scraping statistics

    Example:
        >>> from src.cli import scrape_full_shop
        >>> stats = scrape_full_shop("biedronka", active_only=True)
        >>> stats['leaflets_count']
        5
    """
```

---

## Config Module

### src.config

Configuration management using Pydantic Settings.

### Settings

```python
class Settings(BaseSettings):
    """Application settings."""

    # Paths
    data_dir: Path = Path("data")
    cache_dir: Path = Path("data/cache")

    # WebDriver
    headless: bool = False
    chrome_profile_dir: Optional[str] = None
    window_width: int = 1920
    window_height: int = 1080

    # Scraping
    request_delay_min: float = 2.0
    request_delay_max: float = 5.0
    max_retries: int = 3
    retry_backoff: float = 2.0
    page_load_timeout: int = 30

    # Logging
    log_level: str = "INFO"
    log_format: str = "console"

    # URLs
    base_url: str = "https://blix.pl"
    shops_url: str = "https://blix.pl/sklepy/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
```

**Usage**:
```python
from src.config import settings

# Access settings
print(settings.data_dir)
print(settings.base_url)
print(settings.request_delay_min)
```

---

## Domain Entities

### src.domain.entities

Pydantic models for data validation.

### Shop

```python
class Shop(BaseModel):
    """
    Retail brand entity.

    Attributes:
        slug: URL slug (e.g., 'biedronka')
        name: Display name (e.g., 'Biedronka')
        logo_url: URL to shop logo
        category: Shop category (e.g., 'Sklepy spożywcze')
        leaflet_count: Number of leaflets
        is_popular: Whether shop is popular
        scraped_at: Timestamp of scrape
    """

    slug: str
    name: str
    logo_url: HttpUrl
    category: Optional[str] = None
    leaflet_count: int = 0
    is_popular: bool = False
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "slug": "biedronka",
            "name": "Biedronka",
            "logo_url": "https://img.blix.pl/image/brand/thumbnail_23.jpg",
            "category": "Sklepy spożywcze",
            "leaflet_count": 13,
            "is_popular": True
        }
    })
```

### Leaflet

```python
class LeafletStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    UPCOMING = "upcoming"


class Leaflet(BaseModel):
    """
    Promotional leaflet entity.

    Attributes:
        leaflet_id: Unique identifier
        shop_slug: Shop slug reference
        name: Leaflet name
        cover_image_url: URL to cover image
        url: Leaflet URL
        valid_from: Start date
        valid_until: End date
        status: Leaflet status
        page_count: Number of pages
        scraped_at: Timestamp of scrape
    """

    leaflet_id: int
    shop_slug: str
    name: str
    cover_image_url: HttpUrl
    url: HttpUrl
    valid_from: datetime
    valid_until: datetime
    status: LeafletStatus
    page_count: Optional[int] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    def is_valid_on(self, target_date: datetime) -> bool:
        """Check if leaflet is valid on given date."""
        return self.valid_from <= target_date <= self.valid_until

    def is_active_now(self) -> bool:
        """Check if leaflet is currently active."""
        return self.is_valid_on(datetime.utcnow())
```

### Offer

```python
class Offer(BaseModel):
    """
    Product offer entity.

    Attributes:
        leaflet_id: Parent leaflet reference
        name: Product name
        price: Product price (PLN)
        image_url: Product image URL
        page_number: Page in leaflet
        position_x: Horizontal position (0-1)
        position_y: Vertical position (0-1)
        width: Width fraction (0-1)
        height: Height fraction (0-1)
        valid_from: Offer start date
        valid_until: Offer end date
    """

    leaflet_id: int
    name: str
    price: Optional[Decimal] = None
    image_url: HttpUrl
    page_number: int = 1
    position_x: float = 0.0
    position_y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    valid_from: datetime
    valid_until: datetime
```

### Keyword

```python
class Keyword(BaseModel):
    """
    Product keyword/category tag entity.

    Attributes:
        leaflet_id: Parent leaflet reference
        text: Keyword text
        url: Keyword URL
        category_path: Parsed category path
    """

    leaflet_id: int
    text: str
    url: str
    category_path: str
```

### SearchResult

```python
class SearchResult(BaseModel):
    """
    Search result entity.

    Attributes:
        name: Product name
        price_pln: Price in PLN
        brand_name: Brand name
        shop_name: Shop name
        leaflet_id: Leaflet reference
        page_number: Page in leaflet
    """

    name: str
    price_pln: Optional[Decimal] = None
    brand_name: Optional[str] = None
    shop_name: Optional[str] = None
    leaflet_id: int
    page_number: int = 1
```

---

## Orchestrator

### src.orchestrator

Main orchestrator class for coordinating scraping workflows.

### ScraperOrchestrator

```python
class ScraperOrchestrator:
    """
    Orchestrates scraping workflows.

    Coordinates scrapers and storage operations.

    Usage:
        with ScraperOrchestrator(headless=True) as orchestrator:
            shops = orchestrator.scrape_all_shops()
            leaflets = orchestrator.scrape_shop_leaflets("biedronka")
    """

    def __init__(self, headless: bool = False):
        """
        Initialize orchestrator.

        Args:
            headless: Run Chrome in headless mode
        """
        ...

    def __enter__(self) -> "ScraperOrchestrator":
        """Context manager entry - create driver."""
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup driver."""
        ...

    def scrape_all_shops(self) -> List[Shop]:
        """
        Scrape all shops from main page.

        Returns:
            List of Shop entities
        """
        ...

    def scrape_shop_leaflets(self, shop_slug: str) -> List[Leaflet]:
        """
        Scrape all leaflets for a specific shop.

        Args:
            shop_slug: Shop slug (e.g., 'biedronka')

        Returns:
            List of Leaflet entities
        """
        ...

    def scrape_leaflet_offers(
        self,
        shop_slug: str,
        leaflet_id: int,
        field_filter: Optional[FieldFilter] = None
    ) -> List[Offer]:
        """
        Scrape all offers for a specific leaflet.

        Args:
            shop_slug: Shop slug
            leaflet_id: Leaflet ID
            field_filter: Optional filter for saved JSON fields

        Returns:
            List of Offer entities
        """
        ...

    def scrape_leaflet_keywords(
        self,
        shop_slug: str,
        leaflet_id: int
    ) -> List[Keyword]:
        """
        Scrape keywords for a specific leaflet.

        Args:
            shop_slug: Shop slug
            leaflet_id: Leaflet ID

        Returns:
            List of Keyword entities
        """
        ...

    def search_products(
        self,
        query: str,
        filter_by_name: bool = True,
        field_filter: Optional[FieldFilter] = None
    ) -> List[SearchResult]:
        """
        Search for products across all shops.

        Args:
            query: Search query string
            filter_by_name: Only return products with query in name
            field_filter: Optional filter for saved JSON fields

        Returns:
            List of SearchResult entities
        """
        ...

    def scrape_full_leaflet(
        self,
        shop_slug: str,
        leaflet_id: int
    ) -> tuple[List[Offer], List[Keyword]]:
        """
        Scrape both offers and keywords for a leaflet.

        Args:
            shop_slug: Shop slug
            leaflet_id: Leaflet ID

        Returns:
            Tuple of (offers, keywords)
        """
        ...

    def scrape_all_shop_data(
        self,
        shop_slug: str,
        active_only: bool = True
    ) -> dict:
        """
        Scrape all data for a shop.

        Args:
            shop_slug: Shop slug
            active_only: Only scrape active leaflets

        Returns:
            Dictionary with scraping statistics
        """
        ...
```

---

## Scrapers

### src.scrapers

Scraper classes for different entity types.

### BaseScraper

```python
class BaseScraper(Generic[T]):
    """
    Abstract base scraper using Selenium + BeautifulSoup.

    Template Method pattern for scraping workflow.

    Attributes:
        driver: Selenium WebDriver instance
    """

    def __init__(self, driver: WebDriver):
        """
        Initialize base scraper.

        Args:
            driver: Selenium WebDriver instance
        """
        ...

    def scrape(self, url: str) -> List[T]:
        """
        Execute scraping workflow.

        Args:
            url: URL to scrape

        Returns:
            List of extracted entities
        """
        ...

    @abstractmethod
    def _wait_for_content(self):
        """Wait for page-specific content to load."""
        ...

    @abstractmethod
    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[T]:
        """Extract domain entities from parsed HTML."""
        ...

    def _validate_entities(self, entities: List[T]) -> List[T]:
        """Validate entities (default: pass-through)."""
        ...
```

### ShopScraper

```python
class ShopScraper(BaseScraper[Shop]):
    """
    Scraper for shop/brand listings.

    Extracts shops from https://blix.pl/sklepy/
    """
    ...
```

### LeafletScraper

```python
class LeafletScraper(BaseScraper[Leaflet]):
    """
    Scraper for leaflet listings.

    Args:
        driver: Selenium WebDriver instance
        shop_slug: Shop slug for URL construction
    """
    ...
```

### OfferScraper

```python
class OfferScraper(BaseScraper[Offer]):
    """
    Scraper for product offers.

    Args:
        driver: Selenium WebDriver instance
        leaflet_id: Leaflet ID for context
    """
    ...
```

### KeywordScraper

```python
class KeywordScraper(BaseScraper[Keyword]):
    """
    Scraper for product keywords.

    Args:
        driver: Selenium WebDriver instance
        leaflet_id: Leaflet ID for context
    """
    ...
```

### SearchScraper

```python
class SearchScraper(BaseScraper[SearchResult]):
    """
    Scraper for search results.

    Args:
        driver: Selenium WebDriver instance
        query: Search query
        filter_by_name: Filter results by name
    """
    ...
```

---

## Storage

### src.storage

Data storage classes.

### JSONStorage

```python
class JSONStorage(Generic[T]):
    """
    JSON file storage implementation.

    Uses Pydantic models for validation.

    Usage:
        storage = JSONStorage(
            data_dir=Path("data/shops"),
            model_class=Shop
        )

        # Save single entity
        storage.save(shop, "biedronka.json")

        # Save multiple entities
        storage.save_many(shops, "shops.json")

        # Load entities
        shop = storage.load("biedronka.json")
        all_shops = storage.load_all()
    """

    def __init__(self, data_dir: Path, model_class: Type[BaseModel]):
        """
        Initialize storage.

        Args:
            data_dir: Directory for JSON files
            model_class: Pydantic model class
        """
        ...

    def save(self, entity: BaseModel, filename: str) -> None:
        """
        Save entity to JSON file.

        Args:
            entity: Pydantic model instance
            filename: Target filename
        """
        ...

    def save_many(
        self,
        entities: List[BaseModel],
        filename: str,
        field_filter: Optional[FieldFilter] = None
    ) -> None:
        """
        Save multiple entities to single JSON file.

        Args:
            entities: List of Pydantic models
            filename: Target filename
            field_filter: Optional filter for fields
        """
        ...

    def load(self, filename: str) -> Optional[BaseModel]:
        """
        Load entity from JSON file.

        Args:
            filename: Source filename

        Returns:
            Pydantic model instance or None
        """
        ...

    def load_all(self) -> List[BaseModel]:
        """
        Load all JSON files in directory.

        Returns:
            List of Pydantic model instances
        """
        ...
```

### FieldFilter

```python
class FieldFilter:
    """
    Filter for selective JSON field export.

    Usage:
        # Use predefined filters
        filter_base = FieldFilter.with_dates()
        filter_minimal = FieldFilter.minimal()

        # Custom filter
        filter_custom = FieldFilter.custom("name", "price", "shop_name")

        # Use with storage
        storage.save_many(offers, "offers.json", field_filter=filter_custom)
    """

    def __init__(self, include: set[str]):
        """
        Initialize filter.

        Args:
            include: Set of field names to include
        """
        ...

    @classmethod
    def minimal(cls) -> "FieldFilter":
        """Minimal fields only (name, price, shop)."""
        ...

    @classmethod
    def with_dates(cls) -> "FieldFilter":
        """Include date fields."""
        ...

    @classmethod
    def extended(cls, *fields: str) -> "FieldFilter":
        """Extended fields."""
        ...

    @classmethod
    def custom(cls, *fields: str) -> "FieldFilter":
        """Custom field selection."""
        ...
```

---

## WebDriver

### src.webdriver

WebDriver management.

### DriverFactory

```python
class DriverFactory:
    """
    Factory for creating undetected Chrome WebDriver instances.
    """

    @staticmethod
    def create_driver(
        headless: bool = False,
        user_data_dir: Optional[str] = None,
        window_size: tuple = (1920, 1080)
    ) -> uc.Chrome:
        """
        Create Chrome WebDriver with anti-detection.

        Args:
            headless: Run in headless mode
            user_data_dir: Path to Chrome profile
            window_size: Browser window dimensions

        Returns:
            Configured Chrome WebDriver instance

        Example:
            >>> from src.webdriver import DriverFactory
            >>> driver = DriverFactory.create_driver(headless=True)
            >>> driver.get("https://blix.pl")
            >>> driver.quit()
        """
        ...
```

### Helper Functions

```python
def human_delay(min_sec: float = 2.0, max_sec: float = 5.0) -> None:
    """
    Random delay to simulate human behavior.

    Args:
        min_sec: Minimum delay in seconds
        max_sec: Maximum delay in seconds
    """
    ...


def wait_for_element(
    driver: WebDriver,
    by: By,
    value: str,
    timeout: int = 10
) -> WebElement:
    """
    Wait for element to be present in DOM.

    Args:
        driver: Selenium WebDriver instance
        by: Locator strategy
        value: Selector value
        timeout: Max wait time in seconds

    Returns:
        WebElement if found

    Raises:
        TimeoutException: Element not found
    """
    ...


def scroll_to_bottom(driver: WebDriver, pause_time: float = 1.0) -> None:
    """
    Scroll to bottom of page to trigger lazy loading.

    Args:
        driver: Selenium WebDriver instance
        pause_time: Pause between scrolls (seconds)
    """
    ...
```

---

## Exceptions

### Custom Exceptions

```python
class ScraperError(Exception):
    """Base exception for scraper errors."""
    ...


class ScrapingError(ScraperError):
    """Error during scraping operation."""
    ...


class ParseError(ScraperError):
    """Error parsing HTML content."""
    ...


class ValidationError(ScraperError):
    """Error validating scraped data."""
    ...


class ConfigurationError(ScraperError):
    """Invalid configuration."""
    ...
```

---

## Quick Reference

### Common Patterns

**Basic scraping**:
```python
from src.orchestrator import ScraperOrchestrator

with ScraperOrchestrator(headless=True) as orchestrator:
    leaflets = orchestrator.scrape_shop_leaflets("biedronka")
    for leaflet in leaflets:
        offers = orchestrator.scrape_leaflet_offers("biedronka", leaflet.leaflet_id)
```

**Search and filter**:
```python
from src.orchestrator import ScraperOrchestrator
from src.storage.field_filter import FieldFilter

with ScraperOrchestrator(headless=True) as orchestrator:
    results = orchestrator.search_products(
        "kawa",
        filter_by_name=True,
        field_filter=FieldFilter.minimal()
    )
```

**Custom storage**:
```python
from src.storage.json_storage import JSONStorage
from src.domain.entities import Shop

storage = JSONStorage(
    data_dir=Path("data/shops"),
    model_class=Shop
)

# Load all shops
shops = storage.load_all()
```

---

## Related Documentation

- [User Guide](user-guide.md) - End-user documentation
- [Developer Guide](developer-guide.md) - Contributing guidelines
- [Architecture](architecture.md) - System architecture
