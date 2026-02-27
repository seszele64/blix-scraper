# Change Proposal: Pure Data Refactor

**Feature Branch**: `pure-data-refactor`  
**Issue**: #N/A (Architectural Refactor)  
**Created**: 2026-02-27  
**Status**: Draft  
**Target**: blix-scraper v0.3.0

## Intent

Transform blix-scraper into a pure data-returning library that scrapes and returns domain entities without any persistence responsibilities. This eliminates tight coupling between scraping and storage, simplifies the architecture, and makes the library more testable and reusable.

## Problem Statement

Currently, blix-scraper suffers from tight coupling between scraping logic and storage operations:

1. **ScraperOrchestrator** embeds storage logic in every scrape method - scrapers save data immediately after fetching
2. **CLI commands** like `list-shops` and `list-leaflets` depend entirely on saved JSON files (offline mode)
3. **Storage module** is tightly integrated with the core scraper workflow
4. **Date filtering** relies on `DateFilteredStorage` instead of in-memory filtering
5. **Testing complexity** increases due to storage layer dependencies

This architecture violates the single responsibility principle - scrapers should fetch data, not manage persistence.

## Scope

### In Scope

1. **Remove ScraperOrchestrator**
   - Delete `src/orchestrator.py` entirely
   - Remove all CLI commands that depend on the orchestrator's storage behavior

2. **Eliminate Storage Module**
   - Delete `src/storage/` directory entirely
   - Remove `JSONStorage`, `FieldFilter`, `DateFilteredStorage`
   - Scrapers return entities without saving

3. **Simplify CLI Commands**
   - Remove `list-shops` command (depends on saved shops data)
   - Remove `list-leaflets` command (depends on saved leaflet data)
   - Keep: `scrape-shops`, `scrape-leaflets`, `scrape-offers`, `scrape-full-shop`, `search`, `config`
   - Modify scraping commands to return/display data without saving

4. **New ScraperService**
   - Create `src/services/scraper_service.py` for orchestrating scrape workflows
   - Returns data in-memory without persistence
   - Supports in-memory date filtering

5. **In-Memory Date Filtering**
   - Replace `DateFilteredStorage` with `ScraperService` date filtering
   - Date filter predicates work on in-memory collections

6. **Remove Offline Mode**
   - All commands require live scraping
   - No dependency on pre-saved JSON files

7. **Test Cleanup**
   - Remove `tests/storage/` directory entirely
   - Remove CLI tests that depend on storage (`test_cli.py` - list_shops, list_leaflets)
   - Update `conftest.py` to remove storage-related fixtures

### Out of Scope

- Adding new storage backends (database, API)
- Caching layer
- Background job scheduling
- Web API endpoints
- Rate limiting improvements
- Browser automation improvements

## Success Criteria

### Functional Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| F1 | Scrapers return data without saving | No file I/O in scraper classes |
| F2 | CLI displays scraped data directly | Commands show output without --load flags |
| F3 | Date filtering works in-memory | Filter applied to returned entity lists |
| F4 | ScraperService orchestrates workflows | Multiple scrapes combined without storage |
| F5 | All scraping commands work | Manual testing of each command |

### Technical Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| T1 | Storage module removed | `src/storage/` directory deleted |
| T2 | Orchestrator removed | `src/orchestrator.py` deleted |
| T3 | Storage tests removed | `tests/storage/` directory deleted |
| T4 | Type hints preserved | mypy strict passes |
| T5 | Code coverage maintained | Coverage > 70% |

### Breaking Changes

| ID | Change | Impact |
|----|--------|--------|
| B1 | Remove `ScraperOrchestrator` | All code using orchestrator must migrate |
| B2 | Remove storage module | No persistence capabilities in core |
| B3 | Remove offline commands | `list-shops`, `list-leaflets` no longer available |
| B4 | Remove offline mode | Must scrape to get data |

## Use Cases

### UC-1: Simple Scraping Workflow

**Actor**: Developer using blix-scraper as a library  
**Scenario**:
1. Developer creates ScraperService instance
2. Calls service.scrape_shops() - receives List[Shop]
3. Calls service.scrape_leaflets("biedronka") - receives List[Leaflet]
4. Works entirely in-memory

**Expected Output**: Clean entity lists, no file operations

### UC-2: Date-Filtered Scraping

**Actor**: User wanting only active leaflets  
**Scenario**:
1. User runs: `blix-scraper scrape-leaflets biedronka --active-on "this weekend"`
2. ScraperService fetches all leaflets
3. In-memory filter keeps only active ones
4. Results displayed directly

**Expected Output**: Filtered results without storage dependency

### UC-3: Library Usage

**Actor**: External developer integrating blix-scraper  
**Scenario**:
1. Import ScraperService from blix_scraper
2. Create service with custom driver options
3. Call scrape methods directly
4. Receive domain entities for custom processing

**Expected Output**: Pure data, no file system dependencies

## Technical Approach

### New Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Layer (Typer)                       │
│  scrape-shops, scrape-leaflets, scrape-offers, search       │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      ScraperService                          │
│  - Orchestrates scrapers without storage                    │
│  - In-memory date filtering                                 │
│  - Returns domain entities                                  │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Scraper Classes                           │
│  ShopScraper, LeafletScraper, OfferScraper, etc.           │
│  Return entities without saving                              │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Entities                            │
│  Shop, Leaflet, Offer, Keyword, SearchResult                │
└─────────────────────────────────────────────────────────────┘
```

### Removed Components

| Component | Path | Action |
|-----------|------|--------|
| ScraperOrchestrator | `src/orchestrator.py` | Delete |
| Storage module | `src/storage/` | Delete |
| FieldFilter | `src/storage/field_filter.py` | Delete |
| JSONStorage | `src/storage/json_storage.py` | Delete |
| DateFilteredStorage | `src/storage/date_filtered_storage.py` | Delete |
| Storage tests | `tests/storage/` | Delete |
| CLI offline tests | `tests/cli/test_cli.py` | Remove list tests |
| DateFilterOptions | `src/domain/date_filter.py` | Move to service |

### New Components

| Component | Path | Purpose |
|-----------|------|---------|
| ScraperService | `src/services/scraper_service.py` | Orchestration without storage |
| In-memory filtering | `src/services/date_filter.py` | Date filtering logic |

### CLI Changes

| Command | Before | After |
|---------|--------|-------|
| scrape-shops | Save to JSON | Display in table |
| scrape-leaflets | Save to JSON | Display in table |
| scrape-offers | Save to JSON | Display sample |
| scrape-full-shop | Save all | Display stats |
| search | Save results | Display results |
| list-shops | Load from JSON | **REMOVED** |
| list-leaflets | Load from JSON | **REMOVED** |

### Dependencies

No new dependencies required. Removing storage may allow removing:
- Any JSON-specific libraries if not used elsewhere

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing users | High | Clear migration guide; v0.3.0 bump |
| Loss of offline capability | Medium | Document as future feature if needed |
| Test coverage gaps | Low | Add tests for new service layer |
| CLI command changes | Medium | Update documentation and help text |

## Timeline Estimate

- **Research**: 0.5 days - Analyze current orchestrator usage
- **Implementation**: 3 days - Create service, update CLI, remove storage
- **Testing**: 1 day - Update tests, verify coverage
- **Verification**: 0.5 days - Manual testing, mypy, ruff
- **Total**: ~5 days

## Migration Guide (For Reference)

### Before (Current)

```python
from src.orchestrator import ScraperOrchestrator

with ScraperOrchestrator() as orchestrator:
    shops = orchestrator.scrape_all_shops()
    # Data saved to JSON automatically
```

### After (Refactored)

```python
from src.services import ScraperService

service = ScraperService(headless=True)
shops = service.scrape_shops()
# Returns data directly, no files created
```

### CLI Migration

```bash
# Old workflow
blix-scraper scrape-shops
blix-scraper list-shops

# New workflow
blix-scraper scrape-shops
# Results displayed directly, no second command needed
```

## Acceptance Checklist

- [ ] ScraperOrchestrator removed
- [ ] Storage module deleted
- [ ] CLI commands updated (no offline commands)
- [ ] ScraperService created with date filtering
- [ ] Storage tests removed
- [ ] mypy strict passes
- [ ] Coverage maintained > 70%
- [ ] Documentation updated
- [ ] All scraping commands manually tested
