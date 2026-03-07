# Blix Scraper - Architecture Documentation

## 1. System Overview

### 1.1 Purpose
Lightweight web scraper for blix.pl that extracts:
- Shop information (brands, categories)
- Leaflet metadata (promotional flyers)
- Product offers within leaflets
- Keywords associated with leaflets

**Key Design Decision**: Pure data-returning library - scrapers return in-memory data structures, no persistence layer. Users decide how to handle the data (display, export, store).

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────┐
│           CLI Layer                 │
│  (Typer commands with Rich tables)  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Service Layer                │
│   ScraperService (context manager)  │
│   - get_shops()                     │
│   - get_leaflets()                  │
│   - get_offers()                    │
│   - get_keywords()                  │
│   - search()                        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Scraper Layer                │
│   ShopScraper, LeafletScraper,      │
│   OfferScraper, KeywordScraper,     │
│   SearchScraper                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Domain Layer                  │
│   Entities (Pydantic models)         │
│   Date filtering utilities          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Infrastructure                │
│   WebDriver Factory                 │
│   (undetected-chromedriver)         │
└─────────────────────────────────────┘
```

### 1.3 Data Flow

1. **CLI Layer**: User invokes a command (e.g., `search "kawa"`)
2. **Service Layer**: Creates ScraperService context, dispatches to appropriate scraper
3. **Scraper Layer**: Uses WebDriver to fetch HTML, parses with BeautifulSoup
4. **Domain Layer**: Validates data through Pydantic models, applies date filters
5. **Infrastructure**: WebDriver handles HTTP requests with anti-detection

Data flows upward - scrapers return domain entities to the service, which returns them to the CLI for display.

### 1.4 Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| WebDriver | `undetected-chromedriver` | Bypasses anti-bot detection |
| Driver Management | `webdriver-manager` | Auto-handles Chrome version matching |
| HTML Parsing | `BeautifulSoup4` + `lxml` | Robust, flexible parsing |
| Data Validation | `pydantic` v2 | Type safety, validation |
| Date Handling | `dateutil` + custom filters | Flexible date parsing |
| CLI | `typer` | Modern, type-hinted CLI |
| Output | `rich` | Formatted tables and output |
| Logging | `structlog` | Structured logging |

### 1.5 Design Principles

1. **Pure Data**: Scrapers return domain entities, no built-in storage
2. **Separation of Concerns**: CLI, Service, Scrapers, Domain are independent
3. **Testability**: Real HTML fixtures from actual website
4. **Robustness**: Undetected Chrome handles anti-bot measures
5. **Single Responsibility**: Each scraper handles one entity type

---

## 2. Service Layer

### 2.1 ScraperService

The `ScraperService` is the main entry point for programmatic usage. It manages the WebDriver lifecycle and provides methods for all scraping operations.

```python
from src.services.scraper_service import ScraperService

with ScraperService(headless=True) as service:
    shops = service.get_shops()
    leaflets = service.get_leaflets("biedronka")
    offers = service.get_offers("biedronka", 457727)
    keywords = service.get_keywords("biedronka", 457727)
    results = service.search("kawa")
```

### 2.2 Service Methods

| Method | Description |
|--------|-------------|
| `get_shops()` | Retrieve all available shops |
| `get_leaflets(shop_slug)` | Get leaflets for a shop |
| `get_offers(shop_slug, leaflet_id)` | Get offers from a leaflet |
| `get_keywords(shop_slug, leaflet_id)` | Get keywords for a leaflet |
| `search(query, filter_by_name=True)` | Search products across all shops |
| `scrape_full_shop(shop_slug, active_only=False)` | Scrape all data for a shop |

### 2.3 Context Manager

`ScraperService` implements the context manager protocol to ensure proper WebDriver lifecycle:

```python
with ScraperService(headless=True) as service:
    # WebDriver is initialized
    results = service.search("kawa")
    # WebDriver is automatically quit on exit
```

---

## 3. Scraper Layer

### 3.1 Base Scraper

All scrapers extend `BaseScraper` which provides:
- WebDriver initialization and management
- HTTP request methods (`download`, `download_with_retry`)
- Template method pattern for subclasses

### 3.2 Available Scrapers

| Scraper | Entity | Description |
|---------|--------|-------------|
| `ShopScraper` | `Shop` | Scrapes shop listings |
| `LeafletScraper` | `Leaflet` | Scrapes leaflet metadata |
| `OfferScraper` | `Offer` | Scrapes product offers |
| `KeywordScraper` | `Keyword` | Scrapes product keywords |
| `SearchScraper` | `SearchResult` | Searches products across shops |

### 3.3 Template Method Pattern

```python
class ShopScraper(BaseScraper):
    def download(self, url: str) -> str:
        """Fetch shop page HTML."""
        return self.download_with_retry(url)
    
    def parse(self, html: str) -> list[Shop]:
        """Parse HTML into Shop entities."""
        soup = BeautifulSoup(html, "lxml")
        # Extract shop data...
        return shops
```

---

## 4. Domain Layer

### 4.1 Entities

All data is represented as Pydantic models:

- **Shop**: Retail brand information (slug, name, logo, leaflet count)
- **Leaflet**: Promotional flyer (ID, shop, dates, status)
- **Offer**: Product offer (name, price, brand, position)
- **Keyword**: Product category tag
- **SearchResult**: Combined offer with shop/leaflet info

### 4.2 Date Filtering

The domain layer provides date filtering capabilities:

```python
from src.domain.date_filter import filter_by_date, parse_date

# Filter leaflets by active date
active_leaflets = filter_by_date(leaflets, active_on=date(2026, 2, 27))

# Filter by date range
range_leaflets = filter_by_date(leaflets, valid_from=date(2026, 3, 1), valid_until=date(2026, 3, 31))
```

---

## 5. CLI Layer

### 5.1 Commands

The CLI is built with Typer and provides:

| Command | Description |
|---------|-------------|
| `scrape-shops` | Scrape all shops |
| `scrape-leaflets` | Scrape leaflets for a shop |
| `scrape-offers` | Scrape offers from a leaflet |
| `scrape-full-shop` | Scrape complete shop data |
| `list-shops` | Display shops |
| `list-leaflets` | Display leaflets with date filtering |
| `search` | Search products |
| `config` | Show configuration |

### 5.2 Output

CLI commands use Rich for formatted output:
- Tables for list displays
- Progress indicators for long operations
- Color-coded status messages

---

## 6. Non-Functional Requirements

### 6.1 Performance
- Target: Scrape 50 leaflets/hour (with human-like delays)
- Headless mode: Optional for faster scraping
- Retry logic: 3 attempts with exponential backoff

### 6.2 Reliability
- Error handling: Graceful failure, log errors, continue
- Data validation: Pydantic validation before returning
- Context manager: Ensures WebDriver cleanup

### 6.3 Observability
- Structured logging with context (shop, leaflet_id)
- Progress bars for long operations
- Error summary at end of scraping session

### 6.4 Maintainability
- Type hints everywhere (`mypy --strict`)
- Real HTML fixtures from actual site
- Documentation in code (Google-style docstrings)

---

## 7. Security & Ethics

### 7.1 Scraping Ethics
- Respect `robots.txt`
- Human-like delays (2-5s between requests)
- User-Agent: Realistic Chrome user agent
- Run during off-peak hours

### 7.2 Chrome Profile
- Optional: Use persistent Chrome profile
- Cookies/session management handled by undetected-chrome

---

## 8. Migration from v0.2.x

Version 0.3.0 introduced breaking changes:

### Removed Components
- `ScraperOrchestrator` class
- `src/storage/` directory (JSONStorage, FieldFilter, etc.)
- JSON file persistence

### New Components
- `ScraperService` - pure data-returning service
- Context manager for WebDriver lifecycle
- Search across all shops

### Updated Usage

**Before (v0.2.x)**:
```python
from src.orchestrator import ScraperOrchestrator
from src.storage.field_filter import FieldFilter

orch = ScraperOrchestrator(headless=True)
orch.scrape_shops()
results = orch.search_products("kawa", field_filter=FieldFilter.minimal())
orch.save_to_file("output.json")
```

**After (v0.3.0)**:
```python
from src.services.scraper_service import ScraperService

with ScraperService(headless=True) as service:
    results = service.search("kawa")
    # Process results in-memory
    # User decides how to store/export
```

---

## 9. Future Considerations

### 9.1 Potential Features
- Export helpers (CSV, JSON, Excel)
- Price history tracking
- Notifications (email/Discord webhook)
- Web UI to browse data

### 9.2 Potential Challenges
- Chrome updates breaking driver
  - **Solution**: webdriver-manager auto-updates
- Anti-bot detection
  - **Solution**: undetected-chromedriver + human delays
- Large result sets
  - **Solution**: Pagination, streaming responses
