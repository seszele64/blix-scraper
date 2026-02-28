# Implementation Tasks: Critical Technical Debt Fixes

**Parent Change**: critical-fixes  
**Status**: Draft

## Overview

This document outlines all implementation tasks for the critical technical debt fixes. The goal is to fix deprecated datetime usage, add retry logic with tenacity, implement hierarchical configuration, and create utility functions. Tasks are organized by phase and include testing and verification steps.

---

## Phase 1: Fix Datetime Deprecation

### Task 1.1: Fix datetime.utcnow() in shop_scraper.py

**Description**: Replace deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)` in shop_scraper.py.

**File**: `src/scrapers/shop_scraper.py`

**Steps**:
1. Update import statement: `from datetime import datetime` → `from datetime import datetime, timezone`
2. Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` on line 130

**Acceptance Criteria**:
- [x] Import statement includes timezone
- [x] No datetime.utcnow() remaining in file

### Task 1.2: Fix datetime.utcnow() in leaflet_scraper.py

**Description**: Replace deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)` in leaflet_scraper.py.

**File**: `src/scrapers/leaflet_scraper.py`

**Steps**:
1. Update import statement: `from datetime import datetime` → `from datetime import datetime, timezone`
2. Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` on lines 124 and 152

**Acceptance Criteria**:
- [x] Import statement includes timezone
- [x] Both datetime.utcnow() calls replaced

### Task 1.3: Fix datetime.utcnow() in offer_scraper.py

**Description**: Replace deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)` in offer_scraper.py.

**File**: `src/scrapers/offer_scraper.py`

**Steps**:
1. Update import statement: `from datetime import datetime` → `from datetime import datetime, timezone`
2. Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` on line 161

**Acceptance Criteria**:
- [x] Import statement includes timezone
- [x] datetime.utcnow() replaced

### Task 1.4: Fix datetime.utcnow() in keyword_scraper.py

**Description**: Replace deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)` in keyword_scraper.py.

**File**: `src/scrapers/keyword_scraper.py`

**Steps**:
1. Update import statement: `from datetime import datetime` → `from datetime import datetime, timezone`
2. Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` on line 105

**Acceptance Criteria**:
- [x] Import statement includes timezone
- [x] datetime.utcnow() replaced

### Task 1.5: Verify no remaining datetime.utcnow() usage

**Description**: Search entire codebase for any remaining datetime.utcnow() usage.

**Steps**:
1. Run grep to find any remaining `datetime.utcnow()` occurrences
2. Fix any findings (may include tests)

**Acceptance Criteria**:
- [x] grep finds no datetime.utcnow() in src/
- [x] grep finds no datetime.utcnow() in tests/

---

## Phase 2: Implement Retry Logic with Tenacity

### Task 2.1: Add tenacity dependency

**Description**: Add tenacity library to project dependencies.

**File**: `pyproject.toml`

**Steps**:
1. Add `tenacity>=8.2.0` to project dependencies
2. Run `uv sync` or `pip install tenacity`

**Acceptance Criteria**:
- [x] tenacity in pyproject.toml
- [x] Library importable in project

### Task 2.2: Create nested RetrySettings class

**Description**: Create RetrySettings class in config.py.

**File**: `src/config.py`

**Steps**:
1. Create `RetrySettings` class extending BaseSettings
2. Add fields: max_attempts, backoff_factor, jitter
3. Create `ScrapingSettings` class with nested retry

**Acceptance Criteria**:
- [x] RetrySettings class created
- [x] ScrapingSettings with nested retry created

### Task 2.3: Add retry decorator to BaseScraper.scrape()

**Description**: Apply tenacity retry decorator to the base scraper scrape method.

**File**: `src/scrapers/base.py`

**Steps**:
1. Import tenacity: `from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type`
2. Import settings
3. Apply @retry decorator to scrape() method
4. Configure retry to use settings.scraping.retry values

**Acceptance Criteria**:
- [x] @retry decorator applied to scrape()
- [x] Uses settings for configuration
- [x] Exponential backoff with jitter configured

### Task 2.4: Add backwards compatibility properties to Settings

**Description**: Add property accessors for backwards compatibility with flat config keys.

**File**: `src/config.py`

**Steps**:
1. Add `max_retries` property returning `scraping.retry.max_attempts`
2. Add `retry_backoff` property returning `scraping.retry.backoff_factor`
3. Add __init__ override to handle legacy flat keys from environment

**Acceptance Criteria**:
- [x] settings.max_retries works
- [x] settings.retry_backoff works
- [x] Environment variables with flat keys work

---

## Phase 3: Create Utility Functions

### Task 3.1: Create URL helpers module

**Description**: Create src/utils/url_helpers.py with absolutize_url function.

**File**: `src/utils/url_helpers.py` (new)

**Steps**:
1. Create module with DEFAULT_BASE_URL constant
2. Implement `absolutize_url(url: str, base_url: str | None = None) -> str` function
3. Add docstrings and type hints

**Acceptance Criteria**:
- [x] Function handles relative URLs
- [x] Function handles absolute URLs
- [x] Function handles None base_url (uses default)
- [x] Function handles empty URLs

### Task 3.2: Create soup helpers module

**Description**: Create src/utils/soup_helpers.py with type-safe BeautifulSoup helpers.

**File**: `src/utils/soup_helpers.py` (new)

**Steps**:
1. Implement `get_single_attribute(tag: Tag | None, attr: str) -> str | None` function
2. Implement `get_first_element(soup: BeautifulSoup, selector: str) -> Tag | None` function
3. Add docstrings and type hints

**Acceptance Criteria**:
- [x] Function handles None tags
- [x] Function extracts single value from list attributes
- [x] Type-safe return types

### Task 3.3: Update utils package exports

**Description**: Update src/utils/__init__.py to export new utilities.

**File**: `src/utils/__init__.py`

**Steps**:
1. Add exports for absolutize_url
2. Add exports for soup helpers

**Acceptance Criteria**:
- [x] New functions importable from src.utils

---

## Phase 4: Update Scraper Code to Use Utilities

### Task 4.1: Update shop_scraper.py to use utilities

**Description**: Refactor shop_scraper.py to use new URL utilities.

**File**: `src/scrapers/shop_scraper.py`

**Steps**:
1. Import absolutize_url from utils
2. Replace inline URL absolutization logic with utility call

**Acceptance Criteria**:
- [x] Uses absolutize_url utility
- [x] No duplicate URL handling logic

### Task 4.2: Update leaflet_scraper.py to use utilities

**Description**: Refactor leaflet_scraper.py to use new URL utilities.

**File**: `src/scrapers/leaflet_scraper.py`

**Steps**:
1. Import absolutize_url from utils
2. Replace inline URL absolutization logic with utility call

**Acceptance Criteria**:
- [x] Uses absolutize_url utility

### Task 4.3: Update offer_scraper.py to use utilities

**Description**: Refactor offer_scraper.py to use new URL utilities.

**File**: `src/scrapers/offer_scraper.py`

**Steps**:
1. Import absolutize_url from utils
2. Replace inline URL absolutization logic with utility call
3. Consider using soup_helpers for attribute extraction

**Acceptance Criteria**:
- [x] Uses absolutize_url utility
- [x] Consider using soup_helpers

---

## Phase 5: Testing

### Task 5.1: Create URL helpers tests

**Description**: Create unit tests for URL utilities.

**File**: `tests/utils/test_url_helpers.py` (new)

**Steps**:
1. Create test file
2. Test relativel_url with base
3. Test already absolute URL
4. Test default base URL
5. Test empty URL
6. Test HTTP vs HTTPS handling

**Acceptance Criteria**:
- [x] All tests pass
- [x] Coverage > 90%

### Task 5.2: Create soup helpers tests

**Description**: Create unit tests for soup utilities.

**File**: `tests/utils/test_soup_helpers.py` (new)

**Steps**:
1. Create test file
2. Test get_single_attribute with list
3. Test get_single_attribute with single value
4. Test get_single_attribute with None

**Acceptance Criteria**:
- [x] All tests pass
- [x] Coverage > 90%

### Task 5.3: Add retry logic tests

**Description**: Add tests for retry decorator behavior.

**File**: `tests/scrapers/test_base.py`

**Steps**:
1. Add test for exponential backoff
2. Add test for max attempts
3. Add test for jitter
4. Add test for exception types

**Acceptance Criteria**:
- [x] Retry tests pass
- [x] Config tests pass

### Task 5.4: Add hierarchical config tests

**Description**: Add tests for nested configuration structure.

**File**: `tests/test_config.py`

**Steps**:
1. Add test for nested retry settings
2. Add test for environment variable override
3. Add test for backwards compatibility properties

**Acceptance Criteria**:
- [x] All config tests pass

---

## Phase 6: Validation

### Task 6.1: Run full test suite

**Description**: Run all tests and verify coverage.

**Commands**:
```bash
# Run all tests
uv run pytest

# Check coverage
uv run pytest --cov=src --cov-report=term-missing
```

**Acceptance Criteria**:
- [ ] All tests pass
- [ ] Coverage > 70% overall

### Task 6.2: Run linting

**Description**: Run linting and formatting checks.

**Commands**:
```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

**Acceptance Criteria**:
- [ ] No lint errors
- [ ] Code formatted correctly

### Task 6.3: Run type checking

**Description**: Run mypy type checking.

**Command**:
```bash
uv run mypy src/
```

**Acceptance Criteria**:
- [ ] mypy strict passes
- [ ] Zero type errors related to datetime or config

### Task 6.4: Verify datetime deprecation fix

**Description**: Verify no deprecation warnings.

**Command**:
```bash
# Run Python with warnings
python -W default::DeprecationWarning -c "from src.scrapers.shop_scraper import ShopScraper"
```

**Acceptance Criteria**:
- [ ] No DeprecationWarning for datetime.utcnow

---

## Task Summary

| Phase | Task | Description | Estimated Time |
|-------|------|-------------|----------------|
| 1 | 1.1 | Fix datetime in shop_scraper.py | 0.1 day |
| 1 | 1.2 | Fix datetime in leaflet_scraper.py | 0.1 day |
| 1 | 1.3 | Fix datetime in offer_scraper.py | 0.1 day |
| 1 | 1.4 | Fix datetime in keyword_scraper.py | 0.1 day |
| 1 | 1.5 | Verify no remaining utcnow() | 0.1 day |
| 2 | 2.1 | Add tenacity dependency | 0.1 day |
| 2 | 2.2 | Create RetrySettings class | 0.25 day |
| 2 | 2.3 | Add retry decorator to BaseScraper | 0.25 day |
| 2 | 2.4 | Add backwards compatibility | 0.25 day |
| 3 | 3.1 | Create URL helpers module | 0.25 day |
| 3 | 3.2 | Create soup helpers module | 0.25 day |
| 3 | 3.3 | Update utils exports | 0.1 day |
| 4 | 4.1 | Update shop_scraper to use utilities | 0.1 day |
| 4 | 4.2 | Update leaflet_scraper to use utilities | 0.1 day |
| 4 | 4.3 | Update offer_scraper to use utilities | 0.1 day |
| 5 | 5.1 | Create URL helpers tests | 0.25 day |
| 5 | 5.2 | Create soup helpers tests | 0.25 day |
| 5 | 5.3 | Add retry logic tests | 0.25 day |
| 5 | 5.4 | Add config tests | 0.25 day |
| 6 | 6.1 | Run full test suite | 0.1 day |
| 6 | 6.2 | Run linting | 0.1 day |
| 6 | 6.3 | Run type checking | 0.1 day |
| 6 | 6.4 | Verify deprecation fix | 0.1 day |
| **Total** | | | **2.65 days** |

---

## Verification Checklist

### Pre-Implementation
- [ ] OpenSpec proposal approved
- [ ] All spec files created
- [ ] Design reviewed

### Implementation
- [ ] Phase 1 complete (datetime fixes)
- [ ] Phase 2 complete (retry logic)
- [ ] Phase 3 complete (utility functions)
- [ ] Phase 4 complete (update scrapers)
- [ ] Phase 5 complete (testing)

### Post-Implementation
- [ ] Phase 6 complete (validation)
- [ ] All tests pass
- [ ] Coverage > 70%
- [ ] mypy passes
- [ ] Linting passes
- [ ] No datetime.utcnow() in codebase

---

## Notes

- Task estimates are based on experienced developer implementation
- Datetime fixes are straightforward - mainly import and method changes
- Retry implementation requires careful configuration of tenacity
- Utility functions should be pure and easily testable
- Backwards compatibility is critical for existing users
