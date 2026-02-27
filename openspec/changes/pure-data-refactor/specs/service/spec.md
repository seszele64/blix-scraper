# ScraperService Specifications

**Spec ID**: 01-service  
**Parent Change**: pure-data-refactor  
**Status**: Draft

## Overview

This specification defines the new ScraperService that replaces ScraperOrchestrator. The service provides pure data-returning methods without any storage or persistence responsibilities.

## ADDED Requirements

### Requirement: ScraperService Context Manager

ScraperService SHALL be a context manager that manages WebDriver lifecycle.

#### Scenario: Service initialization and cleanup
- **GIVEN** a ScraperService instance is created with headless=False
- **WHEN** the service is used as a context manager with `with ScraperService() as service:`
- **THEN** a WebDriver is created and assigned to service.driver
- **AND** the service is returned for use
- **WHEN** the context exits
- **THEN** the WebDriver is quit and resources are cleaned up

#### Scenario: Service with headless mode
- **GIVEN** a ScraperService instance is created with headless=True
- **WHEN** the service enters its context manager
- **THEN** a headless WebDriver is created

### Requirement: get_shops() Method

ScraperService SHALL provide get_shops() method that returns List[Shop] without saving.

#### Scenario: Fetch shops from blix.pl
- **GIVEN** a ScraperService is active (inside context manager)
- **WHEN** get_shops() is called
- **THEN** it scrapes shops from settings.shops_url
- **AND** returns a List[Shop] containing all available shops
- **AND** no files are written to disk

#### Scenario: Returns shop entities with all fields
- **GIVEN** a ScraperService is active
- **WHEN** get_shops() is called
- **THEN** each Shop in the returned list has slug, brand_id, name, logo_url, category, leaflet_count, and is_popular populated

### Requirement: get_leaflets(shop_slug) Method

ScraperService SHALL provide get_leaflets(shop_slug) method that returns List[Leaflet] without saving.

#### Scenario: Fetch leaflets for a shop
- **GIVEN** a ScraperService is active
- **WHEN** get_leaflets("biedronka") is called
- **THEN** it scrapes leaflets from the biedronka shop page
- **AND** returns a List[Leaflet] containing all leaflets for that shop
- **AND** no files are written to disk

#### Scenario: Returns leaflet entities with validation dates
- **GIVEN** a ScraperService is active
- **WHEN** get_leaflets("carrefour") is called
- **THEN** each Leaflet in the returned list has valid_from, valid_until, and status fields populated
- **AND** the is_valid_on() and is_active_now() methods work correctly

### Requirement: get_offers(shop, leaflet) Method

ScraperService SHALL provide get_offers(shop, leaflet) method that returns List[Offer] without saving.

#### Scenario: Fetch offers for a leaflet
- **GIVEN** a ScraperService is active
- **AND** a Leaflet entity exists with leaflet_id=123
- **WHEN** get_offers("biedronka", leaflet) is called
- **THEN** it scrapes offers from the leaflet page
- **AND** returns a List[Offer] containing all offers in that leaflet
- **AND** no files are written to disk

#### Scenario: Offers include position metadata
- **GIVEN** a ScraperService is active
- **AND** a Leaflet entity exists
- **WHEN** get_offers(shop, leaflet) is called
- **THEN** each Offer in the returned list has page_number, position_x, position_y, width, and height populated

### Requirement: get_keywords(shop, leaflet) Method

ScraperService SHALL provide get_keywords(shop, leaflet) method that returns List[Keyword] without saving.

#### Scenario: Fetch keywords for a leaflet
- **GIVEN** a ScraperService is active
- **AND** a Leaflet entity exists with leaflet_id=456
- **WHEN** get_keywords("biedronka", leaflet) is called
- **THEN** it scrapes keywords from the leaflet page
- **AND** returns a List[Keyword] containing all keywords
- **AND** no files are written to disk

### Requirement: search(query, ...) Method

ScraperService SHALL provide search(query, ...) method returning List[SearchResult] with in-memory date filtering.

#### Scenario: Search for products
- **GIVEN** a ScraperService is active
- **WHEN** search("kawa") is called
- **THEN** it scrapes search results for "kawa" from blix.pl
- **AND** returns a List[SearchResult] containing matching products
- **AND** no files are written to disk

#### Scenario: Search with name filtering
- **GIVEN** a ScraperService is active
- **WHEN** search("kawa", filter_by_name=True) is called
- **THEN** only products with "kawa" in the name are returned

#### Scenario: Search without name filtering
- **GIVEN** a ScraperService is active
- **WHEN** search("kawa", filter_by_name=False) is called
- **THEN** all offers from leaflets matching "kawa" are returned

#### Scenario: Search with date filtering
- **GIVEN** a ScraperService is active
- **AND** date_filter has active_on set to a specific date
- **WHEN** search("kawa", date_filter=date_filter) is called
- **THEN** only SearchResults from leaflets valid on that date are returned
- **AND** the filtering happens in-memory after scraping

### Requirement: No Storage Interaction

ScraperService SHALL NOT interact with any storage layer.

#### Scenario: No file system writes
- **GIVEN** a ScraperService is active
- **WHEN** any method (get_shops, get_leaflets, get_offers, get_keywords, search) is called
- **THEN** no files are created in data/ or any other directory
- **AND** no JSON serialization occurs

#### Scenario: No storage imports
- **GIVEN** the ScraperService module
- **WHEN** the code is analyzed for imports
- **THEN** there are no imports from src.storage or any storage-related modules

## MODIFIED Requirements

### Requirement: Service Replaces Orchestrator

The ScraperService MUST replace ScraperOrchestrator for all scraping workflows.

#### Scenario: Migrating from orchestrator to service
- **GIVEN** code using ScraperOrchestrator
- **WHEN** migrated to use ScraperService
- **THEN** all scraping functionality works without storage
- **AND** the same entity types (Shop, Leaflet, Offer, Keyword, SearchResult) are returned

### Requirement: Date Filtering In-Memory

Date filtering MUST work in-memory on returned entity collections.

#### Scenario: Filter leaflets by active date
- **GIVEN** get_leaflets() returns a list of Leaflet entities
- **WHEN** date_filter with active_on is applied
- **THEN** only leaflets valid on that date are in the result

#### Scenario: Filter offers by validity range
- **GIVEN** a list of Offer entities
- **WHEN** date filtering is applied with date_from and date_to
- **THEN** only offers with validity overlapping the range are returned

## Implementation Notes

### File Location

- Service implementation: `src/services/scraper_service.py`

### Dependencies

- Uses existing scraper classes: ShopScraper, LeafletScraper, OfferScraper, KeywordScraper, SearchScraper
- Uses existing domain entities from src.domain.entities
- Uses DriverFactory from src.webdriver.driver_factory

### Backward Compatibility

- Returns same entity types as old orchestrator (Shop, Leaflet, Offer, Keyword, SearchResult)
- Context manager pattern matches orchestrator interface

### Interface

```python
class ScraperService:
    def __init__(self, headless: bool = False) -> None: ...
    
    def __enter__(self) -> "ScraperService": ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
    
    def get_shops(self) -> List[Shop]: ...
    
    def get_leaflets(
        self, 
        shop_slug: str,
        date_filter: Optional[DateFilterOptions] = None
    ) -> List[Leaflet]: ...
    
    def get_offers(
        self, 
        shop_slug: str, 
        leaflet: Leaflet
    ) -> List[Offer]: ...
    
    def get_keywords(
        self, 
        shop_slug: str, 
        leaflet: Leaflet
    ) -> List[Keyword]: ...
    
    def search(
        self, 
        query: str, 
        filter_by_name: bool = True,
        date_filter: Optional[DateFilterOptions] = None
    ) -> List[SearchResult]: ...
```
