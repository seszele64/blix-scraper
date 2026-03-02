# Technical Design: Pure Data Refactor

**Parent Change**: pure-data-refactor  
**Status**: Draft

## Technical Approach

### Overview

The refactoring transforms blix-scraper from a save-oriented library (where scraping automatically persists data to JSON files) into a pure data-returning library that scrapes and returns domain entities without any persistence responsibilities.

### Core Principles

1. **Scrapers Return Data, Not Files**: All scraper classes (ShopScraper, LeafletScraper, OfferScraper, etc.) return domain entities without saving to disk.

2. **Service Layer for Orchestration**: A new `ScraperService` coordinates multiple scraper calls and provides in-memory date filtering.

3. **CLI Fetches On-Demand**: All CLI commands scrape and display data directly without reading from saved files.

4. **No Storage Dependencies**: The entire storage module is removed, eliminating tight coupling between scraping and persistence.

### Design Philosophy

The architecture follows the single responsibility principle:
- **Scrapers**: Fetch HTML, parse to entities, return entities
- **Service**: Orchestrate scraper workflows, apply filters
- **CLI**: Parse user input, call service, display results

This separation makes the library more:
- **Testable**: No file I/O mocking required for scraper tests
- **Reusable**: Entities can be used directly without file system dependencies
- **Maintainable**: Clear boundaries between concerns

---

## Architecture Decisions

### Decision 1: Remove Orchestrator Entirely (No Backward Compatibility)

**Description**: Delete `src/orchestrator.py` completely without maintaining any backward compatibility layer.

**Files Affected**:
- `src/orchestrator.py` - Delete
- All CLI commands using `ScraperOrchestrator` - Modify to use `ScraperService`

| Pros | Cons |
|------|------|
| Clean break - no technical debt from maintaining old interface | Existing users must rewrite code using orchestrator |
| Simpler codebase - one less module to maintain | No gradual migration path |
| Forces adoption of new patterns | Requires comprehensive migration guide |
| Eliminates storage logic from orchestration | - |
| Easier to understand the codebase | - |

**Decision**: APPROVED - The orchestrator's main responsibility was coordinating storage, which contradicts the pure-data goal.

---

### Decision 2: Remove Storage Module Entirely

**Description**: Delete the entire `src/storage/` directory including JSONStorage, FieldFilter, and DateFilteredStorage.

**Files Affected**:
- `src/storage/__init__.py` - Delete
- `src/storage/json_storage.py` - Delete
- `src/storage/field_filter.py` - Delete
- `src/storage/date_filtered_storage.py` - Delete
- `tests/storage/` - Delete entire directory

| Pros | Cons |
|------|------|
| Eliminates tight coupling between scraping and storage | No built-in persistence (must implement separately if needed) |
| Simpler architecture - one less layer | Users lose offline capability |
| Easier testing - no file I/O mocking | Must re-scrape to get data |
| Smaller codebase | Loss of existing data files |
| Faster development - less code to maintain | - |

**Decision**: APPROVED - Storage was the source of tight coupling. Removing it achieves the pure-data goal.

---

### Decision 3: Create ScraperService as Thin Coordination Layer

**Description**: Create a new `ScraperService` class that orchestrates scraper calls without any storage logic.

**Files to Create**:
- `src/services/__init__.py`
- `src/services/scraper_service.py`
- `src/services/date_filter.py`

| Pros | Cons |
|------|------|
| Replaces orchestrator functionality cleanly | New module to learn for existing users |
| Returns data without saving | Requires testing new service |
| Provides central place for date filtering | Adds a layer of indirection |
| Context manager for WebDriver lifecycle | - |
| Same interface pattern as old orchestrator | - |

**Decision**: APPROVED - Service layer provides necessary orchestration without storage coupling.

---

### Decision 4: In-Memory Date Filtering Instead of Storage-Based

**Description**: Replace `DateFilteredStorage` with in-memory filtering using `DateFilterOptions.to_predicate()` on returned entity lists.

**Implementation**:
- Date filtering happens in `ScraperService` after scraping
- Uses existing `DateFilterOptions` from `src/domain/date_filter.py`
- Applies predicates to in-memory collections

| Pros | Cons |
|------|------|
| No storage dependency for filtering | Must scrape all data before filtering |
| Works with any entity collection | Memory usage for large datasets |
| Reuses existing date filter logic | - |
| Simpler - one less specialized class | - |

**Decision**: APPROVED - In-memory filtering aligns with pure-data approach and reuses existing date filter code.

---

### Decision 5: Remove Offline CLI Commands (list-shops, list-leaflets)

**Description**: Remove CLI commands that read from saved JSON files: `list-shops` and `list-leaflets`.

**Files Affected**:
- `src/cli/__init__.py` - Remove both command functions
- `tests/cli/test_cli.py` - Remove tests for these commands

| Pros | Cons |
|------|------|
| No dependency on pre-saved data | Users cannot view previously scraped data |
| Simpler CLI - fewer commands to maintain | Loss of offline viewing capability |
| Forces on-demand scraping | Must re-scrape to see data |
| Cleaner architecture | Users expecting offline mode must adapt |

**Decision**: APPROVED - Offline commands contradict the pure-data philosophy.

---

## Data Flow

### New Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User (CLI)                                   │
│  blix-scraper scrape-leaflets biedronka --active-on "this weekend" │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLI Layer (Typer)                                │
│  - src/cli/__init__.py                                             │
│  - Parses CLI arguments                                             │
│  - Creates ScraperService                                           │
│  - Displays results in tables                                       │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ScraperService                                   │
│  - src/services/scraper_service.py                                  │
│  - Context manager for WebDriver                                    │
│  - Orchestrates scraper calls                                       │
│  - Applies in-memory date filtering                                 │
│  - Returns domain entities                                          │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Scraper Classes                                   │
│  - ShopScraper, LeafletScraper, OfferScraper                       │
│  - KeywordScraper, SearchScraper                                   │
│  - src/scrapers/*.py                                                │
│  - Fetch HTML, parse to entities, return entities                   │
│  - NO file I/O                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Domain Entities                                  │
│  - Shop, Leaflet, Offer, Keyword, SearchResult                     │
│  - src/domain/entities.py                                           │
│  - Pure data models (Pydantic)                                     │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DateFilterOptions                                │
│  - src/domain/date_filter.py                                        │
│  - In-memory filtering via predicates                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Sequence Diagram: Scrape Leaflets with Date Filter

```
┌─────────┐     ┌──────────┐     ┌──────────────┐     ┌────────────┐     ┌──────────┐
│  User   │     │   CLI    │     │ScraperService│     │  Scrapers  │     │ Entities │
└────┬────┘     └────┬─────┘     └──────┬───────┘     └──────┬─────┘     └────┬────┘
     │               │                  │                    │                │
     │scrape-leaflets│                  │                    │                │
     │biedronka     │                  │                    │                │
     │--active-on   │                  │                    │                │
     │"this weekend"│                  │                    │                │
     │─────────────>│                  │                    │                │
     │               │                  │                    │                │
     │               │Create service    │                    │                │
     │               │───> ScraperService                   │                │
     │               │                  │                    │                │
     │               │                  │get_shops()        │                │
     │               │                  │───────────────────>│                │
     │               │                  │                    │                │
     │               │                  │<───────────────────│                │
     │               │                  │(List[Shop])        │                │
     │               │                  │                    │                │
     │               │                  │get_leaflets()     │                │
     │               │                  │───────────────────>│                │
     │               │                  │                    │                │
     │               │                  │<───────────────────│                │
     │               │                  │(List[Leaflet])    │                │
     │               │                  │                    │                │
     │               │                  │Apply date filter  │                │
     │               │                  │in-memory           │                │
     │               │                  │──────┐             │                │
     │               │                  │      │             │                │
     │               │                  │<─────┘             │                │
     │               │                  │(filtered list)    │                │
     │               │                  │                    │                │
     │               │Display table     │                    │                │
     │<──────────────│                  │                    │                │
     │               │                  │                    │                │
```

---

## File Changes

### Files to Create

| File | Purpose |
|------|---------|
| `src/services/__init__.py` | Service module exports |
| `src/services/scraper_service.py` | Main ScraperService class |
| `src/services/date_filter.py` | In-memory date filtering (if separate from domain) |

### Files to Modify

| File | Changes |
|------|---------|
| `src/cli/__init__.py` | Replace orchestrator with service; remove list-shops/list-leaflets commands |

### Files to Delete

| File | Reason |
|------|--------|
| `src/orchestrator.py` | Replaced by ScraperService |
| `src/storage/__init__.py` | Storage module removed |
| `src/storage/json_storage.py` | Storage module removed |
| `src/storage/field_filter.py` | Storage module removed |
| `src/storage/date_filtered_storage.py` | Storage module removed |
| `tests/storage/__init__.py` | Storage tests removed |
| `tests/storage/test_json_storage.py` | Storage tests removed |
| `tests/storage/test_field_filter.py` | Storage tests removed |
| `tests/storage/test_date_filtered_storage.py` | Storage tests removed |

---

## Component Mapping

| Old Component | New Component | Status |
|---------------|---------------|--------|
| `ScraperOrchestrator` | `ScraperService` | Replace |
| `JSONStorage` | (removed) | Delete |
| `FieldFilter` | (removed) | Delete |
| `DateFilteredJSONStorage` | `ScraperService` with in-memory filtering | Replace |
| `list-shops` (file reader) | `scrape-shops` (on-demand fetcher) | Replace |
| `list-leaflets` (file reader) | `scrape-leaflets` (on-demand fetcher) | Replace |
| `ShopScraper` | `ShopScraper` | Unchanged |
| `LeafletScraper` | `LeafletScraper` | Unchanged |
| `OfferScraper` | `OfferScraper` | Unchanged |
| `KeywordScraper` | `KeywordScraper` | Unchanged |
| `SearchScraper` | `SearchScraper` | Unchanged |
| Domain entities | Domain entities | Unchanged |
| `DateFilterOptions` | `DateFilterOptions` | Unchanged (moves to service usage) |

---

## Class Diagrams

### New Class Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ScraperService                                  │
├─────────────────────────────────────────────────────────────────────┤
│ - headless: bool                                                    │
│ - driver: WebDriver | None                                         │
├─────────────────────────────────────────────────────────────────────┤
│ + __init__(headless: bool = False)                                  │
│ + __enter__() -> ScraperService                                     │
│ + __exit__(exc_type, exc_val, exc_tb) -> None                       │
│ + get_shops() -> List[Shop]                                         │
│ + get_leaflets(shop_slug: str, date_filter: DateFilterOptions)     │
│   -> List[Leaflet]                                                  │
│ + get_offers(shop_slug: str, leaflet: Leaflet) -> List[Offer]     │
│ + get_keywords(shop_slug: str, leaflet: Leaflet) -> List[Keyword] │
│ + search(query: str, filter_by_name: bool, date_filter:            │
│   DateFilterOptions) -> List[SearchResult]                         │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ uses
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DateFilterOptions                               │
├─────────────────────────────────────────────────────────────────────┤
│ - active_on: datetime | None                                        │
│ - valid_from: datetime | None                                       │
│ - valid_until: datetime | None                                      │
│ - date_from: datetime | None                                        │
│ - date_to: datetime | None                                          │
├─────────────────────────────────────────────────────────────────────┤
│ + has_date_filter() -> bool                                         │
│ + to_predicate() -> Callable[[T], bool]                             │
└─────────────────────────────────────────────────────────────────────┘
```

### New Module Structure

```
src/
├── services/
│   ├── __init__.py          # EXPORTS: ScraperService
│   ├── scraper_service.py   # Main service class
│   └── date_filter.py       # In-memory filtering helpers
├── scrapers/
│   ├── base.py              # (unchanged)
│   ├── shop_scraper.py      # (unchanged)
│   ├── leaflet_scraper.py   # (unchanged)
│   ├── offer_scraper.py     # (unchanged)
│   ├── keyword_scraper.py   # (unchanged)
│   └── search_scraper.py    # (unchanged)
├── domain/
│   ├── entities.py          # (unchanged): Shop, Leaflet, Offer, etc.
│   └── date_filter.py       # (unchanged): DateFilterOptions
├── webdriver/
│   └── driver_factory.py    # (unchanged)
└── cli/
    └── __init__.py          # (modified): Uses ScraperService
```

### Removed Module Structure

```
src/                          # BEFORE              # AFTER (deleted)
├── orchestrator.py          # ScraperOrchestrator  # DELETED
├── storage/                 # Entire module        # DELETED
│   ├── __init__.py
│   ├── json_storage.py
│   ├── field_filter.py
│   └── date_filtered_storage.py
```

---

## Breaking Changes

### API Breaking Changes

| ID | Change | Description | Migration |
|----|--------|-------------|-----------|
| B1 | Remove `ScraperOrchestrator` | Class deleted | Use `ScraperService` instead |
| B2 | Remove `JSONStorage` | Class deleted | No migration available |
| B3 | Remove `FieldFilter` | Class deleted | No migration available |
| B4 | Remove `DateFilteredJSONStorage` | Class deleted | Use in-memory filtering |

### CLI Breaking Changes

| ID | Change | Description | Migration |
|----|--------|-------------|-----------|
| B5 | Remove `list-shops` command | Command deleted | Use `scrape-shops` for live data |
| B6 | Remove `list-leaflets` command | Command deleted | Use `scrape-leaflets` for live data |
| B7 | Remove offline mode | No data directory reading | Always scrape live data |

### Behavioral Breaking Changes

| ID | Change | Description | Impact |
|----|--------|-------------|--------|
| BF1 | No automatic saving | Scraped data not saved to files | Users must implement persistence if needed |
| BF2 | Always online | Commands require internet | No offline viewing |
| BF3 | Date filter location | Filter applied in service, not storage | Same API, different internal location |

### Version Bump Recommendation

**Recommended Version**: v0.3.0

Semantic versioning guidelines suggest:
- MAJOR (v1.0.0): If maintaining full backward compatibility is impossible
- MINOR (v0.3.0): Appropriate for new features with breaking changes to internal APIs

Since the CLI commands (except list-shops/list-leaflets) remain available and functional, a MINOR bump is appropriate.

---

## Testing Strategy

### Unit Tests for ScraperService

```python
# tests/services/test_scraper_service.py

import pytest
from unittest.mock import Mock, patch
from src.services import ScraperService
from src.domain.entities import Shop, Leaflet, LeafletStatus

class TestScraperService:
    
    def test_service_context_manager_creates_driver(self):
        """Service creates and cleans up WebDriver."""
        with ScraperService(headless=True) as service:
            assert service.driver is not None
        
        # After exit, driver should be quit
        service.driver.quit.assert_called_once()
    
    def test_get_shops_returns_list(self):
        """get_shops returns list of Shop entities."""
        with ScraperService() as service:
            shops = service.get_shops()
            
            assert isinstance(shops, list)
            assert all(isinstance(s, Shop) for s in shops)
    
    def test_get_leaflets_no_storage(self):
        """get_leaflets does not write files."""
        with ScraperService() as service:
            leaflets = service.get_leaflets("biedronka")
            
            # Verify no file I/O occurred
            # (would need to mock filesystem checks)
            assert isinstance(leaflets, list)
    
    def test_get_leaflets_with_date_filter(self):
        """get_leaflets filters by date in-memory."""
        from src.domain.date_filter import DateFilterOptions
        from datetime import datetime, timezone
        
        filter_options = DateFilterOptions(
            active_on=datetime(2024, 1, 20, tzinfo=timezone.utc)
        )
        
        with ScraperService() as service:
            leaflets = service.get_leaflets("biedronka", date_filter=filter_options)
            
            # All returned leaflets should be valid on the date
            for leaflet in leaflets:
                assert leaflet.is_valid_on(filter_options.active_on)
```

### Integration Tests for CLI

```python
# tests/cli/test_scraper_service_integration.py

import pytest
from typer.testing import CliRunner
from src.cli import app

runner = CliRunner()

class TestScrapeShops:
    
    def test_scrape_shops_displays_table(self, monkeypatch):
        """scrape-shops displays shops in table."""
        # Mock ScraperService to avoid actual scraping
        mock_shops = [Shop(slug="biedronka", name="Biedronka", ...)]
        
        with patch('src.cli.ScraperService') as MockService:
            mock_instance = MockService.return_value.__enter__.return_value
            mock_instance.get_shops.return_value = mock_shops
            
            result = runner.invoke(app, ["scrape-shops", "--headless"])
            
            assert result.exit_code == 0
            assert "Biedronka" in result.stdout

class TestSearchCommand:
    
    def test_search_with_date_filter(self, monkeypatch):
        """search command passes date filter to service."""
        # Mock ScraperService
        with patch('src.cli.ScraperService') as MockService:
            mock_instance = MockService.return_value.__enter__.return_value
            mock_instance.search.return_value = []
            
            result = runner.invoke(
                app, 
                ["search", "kawa", "--active-on", "this weekend", "--headless"]
            )
            
            # Verify filter was passed
            mock_instance.search.assert_called_once()
            call_kwargs = mock_instance.search.call_args.kwargs
            assert call_kwargs['date_filter'] is not None
```

### Test File Cleanup

| File | Action |
|------|--------|
| `tests/storage/test_json_storage.py` | DELETE |
| `tests/storage/test_field_filter.py` | DELETE |
| `tests/storage/test_date_filtered_storage.py` | DELETE |
| `tests/storage/__init__.py` | DELETE |
| `tests/cli/test_cli.py` | MODIFY - Remove list_shops, list_leaflets tests |

### Coverage Strategy

1. **Service Layer**: Target 80% coverage for `scraper_service.py`
2. **CLI Integration**: Mock ScraperService to test CLI logic without browser
3. **Date Filtering**: Reuse existing tests from `tests/domain/test_date_filter.py`
4. **Scrapers**: Existing scraper tests remain valid (they test parsing, not storage)

### Testing Commands

```bash
# Run service tests
uv run pytest tests/services/ -v

# Run CLI tests (with mocks)
uv run pytest tests/cli/test_scraper_service_integration.py -v

# Run all tests
uv run pytest tests/ -v

# Coverage
uv run pytest tests/ --cov=src/services --cov-report=term-missing
```

---

## Error Handling

### Service-Level Errors

```python
def get_shops(self) -> List[Shop]:
    """Fetch shops from blix.pl."""
    try:
        scraper = ShopScraper(self.driver)
        shops = scraper.scrape(settings.shops_url)
        logger.info("shops_fetched", count=len(shops))
        return shops
    except Exception as e:
        logger.error("shops_fetch_failed", error=str(e))
        raise ScrapingError(f"Failed to fetch shops: {e}") from e
```

### CLI Error Handling

```python
@app.command()
def scrape_shops(headless: bool = False) -> None:
    """Scrape shops from blix.pl"""
    try:
        with ScraperService(headless=headless) as service:
            shops = service.get_shops()
            display_shops_table(shops)
    except ScrapingError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("unexpected_error")
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)
```

### Date Filter Errors

```python
try:
    date_filter = parse_date_options(active_on, valid_from, valid_until, within_range)
except DateParseError as e:
    console.print(f"[yellow]Warning: {e.message}[/yellow]")
    console.print("[dim]Continuing without date filter.[/dim]")
    date_filter = None
```

---

## Logging

### Service Logging

```python
import structlog

logger = structlog.get_logger(__name__)

class ScraperService:
    
    def get_shops(self) -> List[Shop]:
        logger.info("fetching_shops", headless=self.headless)
        
        try:
            scraper = ShopScraper(self.driver)
            shops = scraper.scrape(settings.shops_url)
            
            logger.info(
                "shops_fetched",
                count=len(shops),
                popular_count=sum(1 for s in shops if s.is_popular)
            )
            
            return shops
        except Exception as e:
            logger.error("shops_fetch_failed", error=str(e))
            raise
    
    def get_leaflets(
        self, 
        shop_slug: str,
        date_filter: DateFilterOptions | None = None
    ) -> List[Leaflet]:
        logger.info("fetching_leaflets", shop_slug=shop_slug)
        
        scraper = LeafletScraper(self.driver, shop_slug)
        url = f"{settings.base_url}/sklep/{shop_slug}/"
        leaflets = scraper.scrape(url)
        
        # Apply date filter in-memory
        if date_filter and date_filter.has_date_filter():
            predicate = date_filter.to_predicate()
            leaflets = [leaf for leaf in leaflets if predicate(leaf)]
            logger.info(
                "leaflets_date_filtered",
                total=len(leaflets),
                filtered_from=original_count
            )
        
        return leaflets
```

---

## Configuration

### New Configuration Options

No new configuration required. The service uses existing settings:

```python
from src.config import settings

# Settings used by ScraperService
settings.base_url          # "https://blix.pl"
settings.shops_url         # "https://blix.pl/sklepy/"
settings.request_delay_min # min delay between requests
settings.request_delay_max # max delay between requests
settings.headless          # default headless mode
settings.log_level         # logging level
```

---

## Performance Considerations

1. **No Storage Overhead**: Eliminating JSON serialization improves scraper performance
2. **In-Memory Filtering**: Fast filtering for typical leaflet counts (100-1000s)
3. **Context Manager**: Proper resource cleanup prevents memory leaks
4. **Lazy Evaluation**: Not implemented - future enhancement if needed

### Memory Usage

For typical workloads:
- Shops: ~50-200 entities (small)
- Leaflets: ~10-100 per shop (small to medium)
- Offers: ~100-1000 per leaflet (medium)

In-memory date filtering is appropriate for these dataset sizes.

---

## Migration Guide

### For Library Users

**Before**:
```python
from src.orchestrator import ScraperOrchestrator

with ScraperOrchestrator() as orchestrator:
    shops = orchestrator.scrape_all_shops()
    # Data saved to data/shops/
```

**After**:
```python
from src.services import ScraperService

service = ScraperService()
shops = service.get_shops()
# Data returned directly, no files
```

### For CLI Users

**Before**:
```bash
# Two-step workflow
blix-scraper scrape-shops
blix-scraper list-shops
```

**After**:
```bash
# Single command
blix-scraper scrape-shops
# Data displayed directly
```

---

## Backward Compatibility

This change introduces BREAKING CHANGES:

1. **No ScraperOrchestrator**: Must migrate to ScraperService
2. **No Storage**: No persistence built-in
3. **No Offline Commands**: list-shops, list-leaflets removed

Users requiring persistence must implement their own storage layer using returned entities.

---

## Appendix: File Manifest

### After Refactoring

```
src/
├── __init__.py
├── __main__.py
├── config.py
├── logging_config.py
├── cli/
│   ├── __init__.py          # MODIFIED
│   └── __main__.py
├── domain/
│   ├── __init__.py
│   ├── entities.py          # UNCHANGED
│   └── date_filter.py       # UNCHANGED
├── scrapers/
│   ├── __init__.py
│   ├── base.py              # UNCHANGED
│   ├── shop_scraper.py      # UNCHANGED
│   ├── leaflet_scraper.py   # UNCHANGED
│   ├── offer_scraper.py     # UNCHANGED
│   ├── keyword_scraper.py   # UNCHANGED
│   └── search_scraper.py    # UNCHANGED
├── services/                 # NEW
│   ├── __init__.py          # NEW
│   ├── scraper_service.py   # NEW
│   └── date_filter.py       # NEW (if separate)
├── utils/
│   ├── __init__.py
│   └── date_parser.py       # UNCHANGED
└── webdriver/
    ├── __init__.py
    ├── driver_factory.py    # UNCHANGED
    └── helpers.py           # UNCHANGED

tests/
├── __init__.py
├── conftest.py              # MODIFIED (remove storage fixtures)
├── test_config.py
├── test_logging_config.py
├── cli/
│   ├── __init__.py
│   ├── test_cli.py          # MODIFIED (remove list tests)
│   └── test_date_filtering.py
├── domain/
│   ├── __init__.py
│   ├── test_entities.py
│   └── test_date_filter.py
├── scrapers/
│   ├── __init__.py
│   ├── test_base.py
│   ├── test_shop_scraper.py
│   ├── test_leaflet_scraper.py
│   ├── test_offer_scraper.py
│   ├── test_keyword_scraper.py
│   └── test_search_scraper.py
├── services/                 # NEW
│   ├── __init__.py
│   └── test_scraper_service.py  # NEW
├── utils/
│   ├── __init__.py
│   └── test_date_parser.py
└── fixtures/
    ├── __init__.py
    └── html/
```

(End of file - design.md)
