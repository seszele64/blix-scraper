# Implementation Tasks: Date Filtering Feature

**Parent Change**: date-filtering  
**Status**: Draft

## Overview

This document outlines all implementation tasks for the date filtering feature. Tasks are organized by phase and include testing and verification steps.

---

## Phase 1: Dependencies and Infrastructure

### Task 1.1: Add dateparser Dependency

**Description**: Add the dateparser library to project dependencies.

**File**: `pyproject.toml`

**Steps**:
1. Add `dateparser>=1.1.0` to dependencies section
2. Run `uv sync` to install the new dependency

**Verification**:
```bash
uv run python -c "import dateparser; print(dateparser.__version__)"
```

**Acceptance Criteria**:
- [ ] dateparser installed successfully
- [ ] Can import in Python

---

## Phase 2: Domain Layer

### Task 2.1: Create DateFilterOptions Model

**Description**: Create the DateFilterOptions model in domain layer.

**File**: `src/domain/date_filter.py` (new)

**Steps**:
1. Create `src/domain/date_filter.py`
2. Define `DateFilterOptions` Pydantic model with fields:
   - `active_on: Optional[datetime]`
   - `valid_from: Optional[datetime]`
   - `valid_until: Optional[datetime]`
   - `date_from: Optional[datetime]` (alias: range-start)
   - `date_to: Optional[datetime]` (alias: range-end)
3. Implement `has_date_filter()` method
4. Implement `to_predicate()` method

**Acceptance Criteria**:
- [ ] DateFilterOptions model created
- [ ] has_date_filter() works correctly
- [ ] to_predicate() returns callable predicate

### Task 2.2: Add is_valid_in_range to Leaflet Entity

**Description**: Add range validation method to Leaflet entity.

**File**: `src/domain/entities.py`

**Steps**:
1. Add `is_valid_in_range(start_date, end_date)` method to Leaflet class
2. Implement overlap detection logic:
   - Returns True if `valid_from <= end_date AND valid_until >= start_date`

**Acceptance Criteria**:
- [ ] Method returns True for overlapping range
- [ ] Method returns False for non-overlapping range

### Task 2.3: Add Date Methods to Offer Entity

**Description**: Add date validation methods to Offer entity.

**File**: `src/domain/entities.py`

**Steps**:
1. Add `is_valid_on(target_date)` method to Offer class
2. Add `is_valid_in_range(start_date, end_date)` method to Offer class

**Acceptance Criteria**:
- [ ] is_valid_on works correctly
- [ ] is_valid_in_range works correctly

### Task 2.4: Domain Layer Tests

**Description**: Create unit tests for domain date filtering.

**File**: `tests/domain/test_date_filter.py` (new)

**Steps**:
1. Create test file
2. Add tests for DateFilterOptions
3. Add tests for Leaflet.is_valid_in_range()
4. Add tests for Offer date methods

**Acceptance Criteria**:
- [ ] All domain date methods tested
- [ ] Coverage > 70% for domain/date_filter.py

---

## Phase 3: Date Parsing Utility

### Task 3.1: Create DateParser Service

**Description**: Implement the date parsing service.

**File**: `src/utils/date_parser.py` (new)

**Steps**:
1. Create `src/utils/date_parser.py`
2. Define `DateParseError` exception class
3. Implement `DateParser` class with:
   - `parse(date_string) -> datetime` - Parse single date
   - `parse_range(range_string) -> tuple[datetime, datetime]` - Parse range
   - `validate(date) -> None` - Validate date range
   - `to_utc(date) -> datetime` - Ensure UTC timezone
4. Handle special phrases:
   - "today", "tomorrow", "yesterday"
   - "this weekend", "next weekend"
   - "end of month"

**Acceptance Criteria**:
- [ ] ISO dates parse correctly
- [ ] Natural language dates parse correctly
- [ ] Range parsing works
- [ ] Invalid dates raise DateParseError

### Task 3.2: Date Parser Tests

**Description**: Create unit tests for DateParser.

**File**: `tests/utils/test_date_parser.py` (new)

**Steps**:
1. Create test file with comprehensive test cases
2. Test all date formats
3. Test error cases
4. Test special phrases

**Acceptance Criteria**:
- [ ] All parsing methods tested
- [ ] Error handling tested
- [ ] Coverage > 70%

---

## Phase 4: Storage Layer

### Task 4.1: Create DateFilteredJSONStorage

**Description**: Create storage class with date filtering support.

**File**: `src/storage/date_filtered_storage.py` (new)

**Steps**:
1. Create `src/storage/date_filtered_storage.py`
2. Create `DateFilteredJSONStorage` class extending `JSONStorage`
3. Implement `load_all(date_filter)` method
4. Implement filtered count methods
5. Add logging for filter operations

**Acceptance Criteria**:
- [ ] Extends existing JSONStorage
- [ ] load_all applies date filter
- [ ] Backward compatible (works without filter)

### Task 4.2: Storage Layer Tests

**Description**: Create tests for date filtered storage.

**File**: `tests/storage/test_date_filtered_storage.py` (new)

**Steps**:
1. Create test file
2. Create test fixtures
3. Test filtered load operations
4. Test count operations

**Acceptance Criteria**:
- [ ] All storage methods tested
- [ ] Coverage > 70%

---

## Phase 5: CLI Integration

### Task 5.1: Update list-leaflets Command

**Description**: Add date filtering options to list-leaflets command.

**File**: `src/cli/__init__.py`

**Steps**:
1. Import DateFilterOptions and DateParser
2. Add new CLI options:
   - `--active-on` / `-a`
   - `--valid-from` / `-f`
   - `--valid-until` / `-u`
   - `--within-range` / `-r`
3. Implement date parsing in command
4. Apply filter to loaded leaflets
5. Update output to show filter info
6. Handle error cases with helpful messages

**Acceptance Criteria**:
- [ ] All date options work
- [ ] Natural language dates parse
- [ ] Error messages are helpful

### Task 5.2: Update search Command

**Description**: Add date filtering options to search command.

**File**: `src/cli/__init__.py`

**Steps**:
1. Add same date options to search command
2. Implement leaflet pre-filtering
3. Search within filtered leaflets

**Acceptance Criteria**:
- [ ] Date filtering works with search
- [ ] Results filtered by leaflet validity

### Task 5.3: CLI Tests

**Description**: Create integration tests for CLI commands.

**File**: `tests/cli/test_date_filtering.py` (new)

**Steps**:
1. Create CLI test file
2. Add tests for list-leaflets with date filters
3. Add tests for search with date filters
4. Test error handling

**Acceptance Criteria**:
- [ ] CLI commands work with filters
- [ ] Error cases handled properly

---

## Phase 6: Integration and Verification

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
- [ ] All tests pass
- [ ] Coverage > 70% for new code
- [ ] No regressions in existing tests

### Task 6.2: Type Checking

**Description**: Run mypy type checking.

**Command**:
```bash
uv run mypy src/
```

**Acceptance Criteria**:
- [ ] mypy strict passes
- [ ] No new type errors

### Task 6.3: Linting

**Description**: Run linting and formatting checks.

**Commands**:
```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

**Acceptance Criteria**:
- [ ] No lint errors
- [ ] Code formatted correctly

### Task 6.4: Manual Testing

**Description**: Test CLI commands manually.

**Commands**:
```bash
# Test with scraped data
blix-scraper list-leaflets biedronka --active-on "2024-01-20"
blix-scraper list-leaflets biedronka --valid-from "next week"
blix-scraper list-leaflets carrefour --within-range "2024-02-01 to 2024-02-14"

# Test search with date filter
blix-scraper search kawa --active-on "this weekend"

# Test error handling
blix-scraper list-leaflets biedronka --active-on "not-a-date"
```

**Acceptance Criteria**:
- [ ] Commands execute without errors
- [ ] Results are correctly filtered
- [ ] Error messages are helpful

---

## Task Summary

| Phase | Task | Description | Estimated Time |
|-------|------|-------------|----------------|
| 1 | 1.1 | Add dateparser dependency | 0.25 day |
| 2 | 2.1 | Create DateFilterOptions model | 0.25 day |
| 2 | 2.2 | Add is_valid_in_range to Leaflet | 0.25 day |
| 2 | 2.3 | Add date methods to Offer | 0.25 day |
| 2 | 2.4 | Domain layer tests | 0.5 day |
| 3 | 3.1 | Create DateParser service | 0.5 day |
| 3 | 3.2 | DateParser tests | 0.5 day |
| 4 | 4.1 | Create DateFilteredJSONStorage | 0.5 day |
| 4 | 4.2 | Storage layer tests | 0.5 day |
| 5 | 5.1 | Update list-leaflets command | 0.5 day |
| 5 | 5.2 | Update search command | 0.25 day |
| 5 | 5.3 | CLI tests | 0.5 day |
| 6 | 6.1 | Run test suite | 0.25 day |
| 6 | 6.2 | Type checking | 0.25 day |
| 6 | 6.3 | Linting | 0.25 day |
| 6 | 6.4 | Manual testing | 0.25 day |
| **Total** | | | **5.5 days** |

---

## Verification Checklist

### Pre-Implementation
- [ ] OpenSpec proposal approved
- [ ] All spec files created
- [ ] Design reviewed

### Implementation
- [ ] Phase 1 complete (dependency)
- [ ] Phase 2 complete (domain)
- [ ] Phase 3 complete (date parser)
- [ ] Phase 4 complete (storage)
- [ ] Phase 5 complete (CLI)

### Post-Implementation
- [ ] All tests pass
- [ ] Coverage > 70%
- [ ] mypy passes
- [ ] Linting passes
- [ ] Manual testing complete
- [ ] Backward compatibility verified
- [ ] Documentation updated

---

## Notes

- Task estimates are based on experienced developer implementation
- Some tasks can be done in parallel (e.g., tests while implementing)
- Manual testing is critical for CLI usability
- Error message quality is important for user experience
