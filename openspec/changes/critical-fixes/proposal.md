# Change Proposal: Critical Technical Debt Fixes

**Feature Branch**: `critical-fixes`  
**Issue**: #N/A (Architectural Technical Debt)  
**Created**: 2026-02-28  
**Status**: Draft  
**Target**: blix-scraper v0.2.1

## Intent

Fix critical technical debt issues in blix-scraper including deprecated datetime usage, missing retry logic, hierarchical configuration, and utility function consolidation. This ensures compliance with Python 3.11+ standards, improves reliability through retry mechanisms, reduces code duplication, and resolves 61 mypy errors.

## Problem Statement

The blix-scraper project currently suffers from several critical technical debt issues:

1. **Deprecated datetime.utcnow()**: Python 3.12+ deprecation warnings across 6 files (scrapers and entities)
2. **Missing Retry Logic**: No retry mechanism for failed HTTP requests, causing fragility in production
3. **Flat Configuration Structure**: Current config lacks hierarchical organization, making it difficult to add nested settings
4. **Code Duplication**: Repeated URL absolutization and date handling logic across multiple scrapers

These issues:
- Cause runtime deprecation warnings
- Lead to mypy strict mode failures (61 errors)
- Create maintenance burden
- Violate the Constitution's requirement for retry logic with exponential backoff

## Scope

### In Scope

1. **Fix datetime.utcnow() Deprecation**
   - Replace deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)` in all affected files
   - Affected files:
     - `src/scrapers/shop_scraper.py`
     - `src/scrapers/leaflet_scraper.py`
     - `src/scrapers/offer_scraper.py`
     - `src/scrapers/keyword_scraper.py`
     - `src/domain/entities.py` (already fixed)
     - `tests/` (if any usage found)

2. **Implement Retry Logic with Tenacity**
   - Add tenacity library for retry handling
   - Apply retry decorator to `BaseScraper.scrape()` method
   - Configure exponential backoff with jitter
   - Make retry settings configurable via hierarchical config

3. **Create Hierarchical Configuration Structure**
   - Nest retry settings under `scraping.retry`
   - Nest scraping settings under `scraping`
   - Add backwards compatibility properties for existing flat config
   - Support environment variable override with `__` delimiter (e.g., `SCRAPING__RETRY__MAX_ATTEMPTS`)

4. **Create Utility Functions**
   - URL absolutization function in `src/utils/url_helpers.py`
   - Fix existing `DateParser` class usage patterns
   - Type-safe BeautifulSoup handling helpers

### Out of Scope

- Refactoring the orchestrator or storage layers
- Adding new scraper types
- Web API endpoints
- Database integration
- Caching layer
- Background job scheduling

## Success Criteria

### Functional Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| F1 | datetime.utcnow() replaced with datetime.now(timezone.utc) | No deprecation warnings in Python 3.12 |
| F2 | Retry logic applies to BaseScraper.scrape() | Failed requests are retried automatically |
| F3 | Retry settings configurable | Can set max_attempts via config/env var |
| F4 | Configuration is hierarchical | Nested settings accessible via dot notation |
| F5 | URL utilities reduce duplication | Common URL logic centralized |

### Technical Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| T1 | mypy strict passes | Zero type errors |
| T2 | No deprecated datetime usage | grep finds no utcnow() |
| T3 | Tenacity integrated | Library imported and used |
| T4 | Backwards compatibility | Existing config keys still work |
| T5 | Test coverage maintained | Coverage > 70% |

### Breaking Changes

| ID | Change | Impact |
|----|--------|--------|
| B1 | Config key changes | Old flat keys deprecated but still functional |

## Use Cases

### UC-1: Scraping with Automatic Retry

**Actor**: Developer running scraper in production  
**Scenario**:
1. Developer runs `blix-scraper scrape-shops`
2. Network timeout occurs on first request
3. Tenacity retries with exponential backoff
4. Request succeeds on second attempt

**Expected Output**: Successful scrape despite transient failures

### UC-2: Configuration via Environment Variables

**Actor**: DevOps engineer configuring container deployment  
**Scenario**:
1. Set environment variable `SCRAPING__RETRY__MAX_ATTEMPTS=5`
2. Start scraper container
3. Scraper uses 5 retry attempts

**Expected Output**: Configuration picked up from environment

### UC-3: URL Handling Utility

**Actor**: Developer adding new scraper  
**Scenario**:
1. Developer creates new scraper class
2. Uses `absolutize_url()` from utils
3. No need to duplicate URL handling logic

**Expected Output**: Consistent URL handling across scrapers

## Technical Approach

### New Architecture

```
src/
├── config.py              # Hierarchical config with backwards compat
├── scrapers/
│   ├── base.py           # Retry logic added via tenacity
│   └── ...
├── utils/
│   ├── __init__.py       # Export utilities
│   ├── url_helpers.py    # NEW: URL absolutization
│   └── date_parser.py    # Existing (unmodified)
```

### Dependencies

Add to `pyproject.toml`:
- `tenacity` - Retry logic library

### Configuration Structure

```python
class ScrapingSettings(BaseSettings):
    """Hierarchical scraping settings."""
    
    request_delay_min: float = 2.0
    request_delay_max: float = 5.0
    page_load_timeout: int = 30
    
    class retry(BaseSettings):
        """Retry configuration nested under scraping."""
        
        max_attempts: int = 3
        backoff_factor: float = 2.0
        jitter: bool = True
```

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Config breaking changes | Medium | Add backwards compatibility properties |
| Test coverage gaps | Low | Add tests for retry logic and utilities |
| Dependency bloat | Low | Tenacity is lightweight |
| mypy migration | Medium | Fix all 61 errors systematically |

## Timeline Estimate

- **Research**: 0.25 days - Analyze current issues
- **Implementation**: 1.5 days - Fix datetime, add retry, update config
- **Testing**: 0.5 days - Verify fixes, add utility tests
- **Verification**: 0.25 days - Run mypy, ruff, pytest
- **Total**: ~2.5 days

## Acceptance Checklist

- [ ] datetime.utcnow() replaced in all files
- [ ] Tenacity integrated into BaseScraper
- [ ] Hierarchical config implemented
- [ ] Backwards compatibility maintained
- [ ] URL utilities created
- [ ] mypy strict passes
- [ ] Tests pass
- [ ] Coverage maintained > 70%
