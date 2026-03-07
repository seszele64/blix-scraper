# Implementation Tasks: Pure Data Refactor

**Parent Change**: pure-data-refactor  
**Status**: Draft

## Overview

This document outlines all implementation tasks for the pure-data-refactor change. The goal is to simplify the architecture by removing the storage layer and orchestrator, and creating a lightweight service layer for on-demand data fetching. Tasks are organized by phase and include testing and verification steps.

---

## Phase 1: Remove Storage and Orchestrator

### Task 1.1: Delete Storage Directory

**Description**: Remove the entire storage module as data will no longer be persisted.

**File**: `src/storage/` (delete)

**Steps**:
1. Remove `src/storage/__init__.py`
2. Remove `src/storage/json_storage.py`
3. Remove any other files in `src/storage/`
4. Remove the empty `src/storage/` directory

**Acceptance Criteria**:
- [x] Storage directory completely removed
- [x] No orphaned imports in other files

### Task 1.2: Delete Orchestrator Module

**Description**: Remove the orchestrator module as its functionality will be replaced by the service layer.

**File**: `src/orchestrator.py` (delete)

**Steps**:
1. Delete `src/orchestrator.py`
2. Verify no remaining references to orchestrator

**Acceptance Criteria**:
- [x] Orchestrator file removed
- [x] No import errors from other modules

### Task 1.3: Remove Storage Imports from CLI

**Description**: Clean up CLI imports that reference storage modules.

**File**: `src/cli/__init__.py`

**Steps**:
1. Remove import statements for storage modules
2. Remove import statements for orchestrator
3. Clean up any related constants or configurations

**Acceptance Criteria**:
- [x] Storage imports removed
- [x] Orchestrator imports removed
- [x] CLI still functions (will be updated in Phase 3)

### Task 1.4: Delete Storage Tests

**Description**: Remove storage-related test files as the storage layer is being removed.

**File**: `tests/storage/` (delete)

**Steps**:
1. Remove all files in `tests/storage/`
2. Remove the empty `tests/storage/` directory

**Acceptance Criteria**:
- [x] Storage test directory removed
- [x] No orphaned imports in other test files

---

## Phase 2: Create Service Layer

### Task 2.1: Create Services Package

**Description**: Create the services package directory and init file.

**File**: `src/services/__init__.py` (new)

**Steps**:
1. Create `src/services/` directory
2. Create `src/services/__init__.py` with package exports

**Acceptance Criteria**:
- [x] Package created successfully
- [x] Can be imported

### Task 2.2: Create ScraperService Class

**Description**: Create the main service class that handles scraping operations.

**File**: `src/services/scraper_service.py` (new)

**Steps**:
1. Create `src/services/scraper_service.py`
2. Define `ScraperService` class with:
   - `__init__(config: Config)` - Initialize with config
   - `get_shops() -> list[Shop]` - Fetch all shops
   - `get_leaflets(shop: Shop) -> list[Leaflet]` - Fetch leaflets for a shop
   - `search_offers(query: str, leaflets: list[Leaflet]) -> list[Offer]` - Search offers
   - `get_all_data() -> ScrapedData` - Fetch all data
3. Implement caching logic for repeated access
4. Add structured logging

**Acceptance Criteria**:
- [x] ScraperService class created
- [x] All methods functional
- [x] Proper error handling

### Task 2.3: Create DateFilterService Class

**Description**: Create service for in-memory date filtering of offers.

**File**: `src/services/date_filter.py` (new)

**Steps**:
1. Create `src/services/date_filter.py`
2. Define `DateFilterService` class with:
   - `filter_by_active_date(offers: list[Offer], date: datetime) -> list[Offer]` - Filter by active date
   - `filter_by_date_range(offers: list[Offer], start: datetime, end: datetime) -> list[Offer]` - Filter by range
   - `filter_leaflets_by_date(leaflets: list[Leaflet], filter_options: DateFilterOptions) -> list[Leaflet]` - Filter leaflets
3. Implement efficient in-memory filtering
4. Add logging for filter operations

**Acceptance Criteria**:
- [x] DateFilterService class created
- [x] All filtering methods work correctly
- [x] Handles edge cases (empty results, invalid dates)

### Task 2.4: Update Services Package Exports

**Description**: Update the services package to export all public classes.

**File**: `src/services/__init__.py`

**Steps**:
1. Add `__all__` list with exports
2. Import and re-export `ScraperService`
3. Import and re-export `DateFilterService`

**Acceptance Criteria**:
- [x] `__all__` defined
- [x] All classes exportable from package

---

## Phase 3: Refactor CLI

### Task 3.1: Update CLI Imports

**Description**: Update CLI to import from the new service layer.

**File**: `src/cli/__init__.py`

**Steps**:
1. Add import for `ScraperService` from `src.services`
2. Add import for `DateFilterService` from `src.services`
3. Remove any remaining old imports

**Acceptance Criteria**:
- [x] Imports work correctly
- [x] No import errors

### Task 3.2: Refactor list-shops Command

**Description**: Update list-shops command to fetch data on-demand instead of from storage.

**File**: `src/cli/__init__.py`

**Steps**:
1. Update `list_shops` callback to use `ScraperService.get_shops()`
2. Remove any storage-related code
3. Add loading indicator for network requests
4. Update output formatting

**Acceptance Criteria**:
- [x] Command fetches shops on-demand
- [x] Results displayed correctly
- [x] Error handling for network failures

### Task 3.3: Refactor list-leaflets Command

**Description**: Update list-leaflets command to fetch data on-demand.

**File**: `src/cli/__init__.py`

**Steps**:
1. Update `list_leaflets` callback to use `ScraperService.get_leaflets()`
2. Integrate `DateFilterService` for date filtering
3. Remove JSONStorage usage
4. Update output formatting

**Acceptance Criteria**:
- [x] Command fetches leaflets on-demand
- [x] Date filtering works (if previously implemented)
- [x] Error handling for network failures

### Task 3.4: Refactor search Command

**Description**: Update search command to use in-memory date filtering.

**File**: `src/cli/__init__.py`

**Steps**:
1. Update search to fetch all data on-demand
2. Implement in-memory filtering using `DateFilterService`
3. Remove storage dependency
4. Optimize for large result sets

**Acceptance Criteria**:
- [x] Command searches on-demand data
- [x] Date filtering works correctly
- [x] Results filtered in-memory

---

## Phase 4: Update Domain and Config

### Task 4.1: Update Package Exports

**Description**: Update main package to export the new service layer.

**File**: `src/__init__.py`

**Steps**:
1. Add export for `ScraperService`
2. Add export for `DateFilterService`
3. Update any existing exports

**Acceptance Criteria**:
- [x] Services exportable from main package
- [x] Backward compatible with existing imports

### Task 4.2: Review Config Dependencies

**Description**: Review and potentially simplify config to remove data_dir dependencies.

**File**: `src/config.py`

**Steps**:
1. Identify any `data_dir` references
2. Remove or mark as deprecated if no longer needed
3. Update config validation

**Acceptance Criteria**:
- [x] Config cleaned up
- [x] No broken references

### Task 4.3: Update pyproject.toml

**Description**: Review and update project dependencies if needed.

**File**: `pyproject.toml`

**Steps**:
1. Check if any dependencies can be removed (storage-related)
2. Verify remaining dependencies
3. Update version if needed

**Acceptance Criteria**:
- [x] Dependencies accurate
- [x] No broken references

---

## Phase 5: Testing

### Task 5.1: Create ScraperService Tests

**Description**: Create unit tests for the new ScraperService.

**File**: `tests/services/test_scraper_service.py` (new)

**Steps**:
1. Create test file
2. Create test fixtures
3. Test `get_shops()` method
4. Test `get_leaflets()` method
5. Test `search_offers()` method
6. Test error handling and edge cases

**Acceptance Criteria**:
- [x] All methods tested
- [x] Coverage > 70% for service
- [x] Mock external dependencies

### Task 5.2: Create DateFilterService Tests

**Description**: Create unit tests for the DateFilterService.

**File**: `tests/services/test_date_filter.py` (new)

**Steps**:
1. Create test file
2. Create test fixtures
3. Test `filter_by_active_date()`
4. Test `filter_by_date_range()`
5. Test `filter_leaflets_by_date()`
6. Test edge cases

**Acceptance Criteria**:
- [x] All filtering methods tested
- [x] Coverage > 70% for service
- [x] Edge cases handled

### Task 5.3: Update Existing Tests

**Description**: Update existing tests to work with the new service layer.

**Files**: `tests/cli/`, `tests/domain/`, etc.

**Steps**:
1. Review existing tests
2. Update imports to use new services
3. Fix any broken tests
4. Remove tests for removed functionality

**Acceptance Criteria**:
- [x] Existing tests pass or updated
- [x] No orphaned test code

### Task 5.4: Remove Orchestrator Tests

**Description**: Remove tests for the removed orchestrator module.

**Files**: `tests/test_orchestrator.py` (if exists)

**Steps**:
1. Identify orchestrator test files
2. Remove them
3. Verify no orphaned references

**Acceptance Criteria**:
- [x] Orchestrator tests removed
- [x] Test suite still runs

---

## Phase 6: Validation

### Task 6.1: Run Full Test Suite

**Description**: Run all tests and verify coverage.

**Commands**:
```bash
# Run all tests
uv run pytest

# Check coverage
uv run pytest --cov=src --cov-report=term-missing
```

**Acceptance Criteria**:
- [x] All tests pass
- [x] Coverage > 70% overall
- [x] No regressions in existing tests

### Task 6.2: Run Linting

**Description**: Run linting and formatting checks.

**Commands**:
```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

**Acceptance Criteria**:
- [x] No lint errors
- [x] Code formatted correctly

### Task 6.3: Run Type Checking

**Description**: Run mypy type checking.

**Command**:
```bash
uv run mypy src/
```

**Acceptance Criteria**:
- [x] mypy strict passes
- [x] No new type errors

### Task 6.4: Verify CLI Commands Work

**Description**: Test CLI commands manually to ensure they function correctly.

**Commands**:
```bash
# Test list-shops
blix-scraper list-shops

# Test list-leaflets (with existing shop name)
blix-scraper list-leaflets biedronka

# Test search
blix-scraper search kawa

# Test error handling
blix-scraper list-leaflets invalid-shop
```

**Acceptance Criteria**:
- [x] list-shops works
- [x] list-leaflets works
- [x] search works
- [x] Error messages are helpful

---

## Task Summary

| Phase | Task | Description | Estimated Time |
|-------|------|-------------|----------------|
| 1 | 1.1 | Delete storage directory | 0.25 day |
| 1 | 1.2 | Delete orchestrator module | 0.25 day |
| 1 | 1.3 | Remove storage imports from CLI | 0.25 day |
| 1 | 1.4 | Delete storage tests | 0.25 day |
| 2 | 2.1 | Create services package | 0.25 day |
| 2 | 2.2 | Create ScraperService class | 0.5 day |
| 2 | 2.3 | Create DateFilterService class | 0.5 day |
| 2 | 2.4 | Update services package exports | 0.25 day |
| 3 | 3.1 | Update CLI imports | 0.25 day |
| 3 | 3.2 | Refactor list-shops command | 0.5 day |
| 3 | 3.3 | Refactor list-leaflets command | 0.5 day |
| 3 | 3.4 | Refactor search command | 0.5 day |
| 4 | 4.1 | Update package exports | 0.25 day |
| 4 | 4.2 | Review config dependencies | 0.25 day |
| 4 | 4.3 | Update pyproject.toml | 0.25 day |
| 5 | 5.1 | Create ScraperService tests | 0.5 day |
| 5 | 5.2 | Create DateFilterService tests | 0.5 day |
| 5 | 5.3 | Update existing tests | 0.5 day |
| 5 | 5.4 | Remove orchestrator tests | 0.25 day |
| 6 | 6.1 | Run full test suite | 0.25 day |
| 6 | 6.2 | Run linting | 0.25 day |
| 6 | 6.3 | Run type checking | 0.25 day |
| 6 | 6.4 | Verify CLI commands work | 0.25 day |
| **Total** | | | **7.75 days** |

---

## Verification Checklist

### Pre-Implementation
- [ ] OpenSpec proposal approved
- [ ] All spec files created
- [ ] Design reviewed

### Implementation
- [ ] Phase 1 complete (remove storage and orchestrator)
- [ ] Phase 2 complete (create service layer)
- [ ] Phase 3 complete (refactor CLI)
- [ ] Phase 4 complete (update domain and config)
- [ ] Phase 5 complete (testing)

### Post-Implementation
- [ ] Phase 6 complete (validation)
- [ ] All tests pass
- [ ] Coverage > 70%
- [ ] mypy passes
- [ ] Linting passes
- [ ] Manual testing complete
- [ ] CLI commands work correctly
- [ ] Documentation updated

---

## Notes

- Task estimates are based on experienced developer implementation
- Some tasks can be done in parallel (e.g., tests while implementing)
- Manual testing is critical for CLI usability
- Consider caching strategies for frequently accessed data
- Error message quality is important for user experience

