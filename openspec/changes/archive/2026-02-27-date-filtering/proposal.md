# Change Proposal: Date Filtering Feature

**Feature Branch**: `date-filtering`  
**Issue**: #3  
**Created**: 2026-02-27  
**Status**: Draft  
**Target**: blix-scraper v0.2.0

## Problem Statement

Currently, the blix-scraper stores and retrieves promotional leaflets and offers but lacks the ability to filter them by validity dates. Users need to:

1. Find leaflets that are valid on a specific date (e.g., "what's available this weekend?")
2. Filter offers by leaflet validity period
3. Query data within a date range

The domain entities (`Leaflet`, `Offer`) already have `valid_from` and `valid_until` datetime fields, but there are no CLI commands or filtering mechanisms to leverage this data for queries.

## Scope

### In Scope

1. **CLI Commands**: New commands to filter leaflets/offers by date
   - `list-leaflets` with `--active-on`, `--valid-from`, `--valid-until`, `--within-range` options
   - `search` command with date filtering options
   - Date filtering integration with existing `list_shops`, `list_leaflets` commands

2. **Repository Layer**: Filtering capabilities in the data access layer
   - Date range filtering for Leaflet entities
   - Filter offers by associated leaflet dates

3. **Domain Logic**: Date filtering utilities
   - `is_valid_on()` method enhancement (already exists on Leaflet)
   - New filtering service/class for date-based queries

4. **Date Parsing**: Flexible date input handling
   - Integration with `dateparser` library for natural language dates
   - Support for common formats: "2024-01-15", "next Friday", "tomorrow"

### Out of Scope

- Scheduled scraping jobs (future feature)
- Push notifications for new leaflets (future feature)
- Web dashboard (future feature)
- Price range filtering (separate feature)
- Fuzzy search (separate feature)

## Success Criteria

### Functional Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| F1 | User can list leaflets valid on a specific date | `blix-scraper list-leaflets biedronka --active-on "2024-01-20"` |
| F2 | User can list leaflets valid from a specific date | `blix-scraper list-leaflets biedronka --valid-from "next week"` |
| F3 | User can list leaflets valid until a specific date | `blix-scraper list-leaflets biedronka --valid-until "end of month"` |
| F4 | User can list leaflets within a date range | `blix-scraper list-leaflets biedronka --within-range "2024-01-01 to 2024-01-31"` |
| F5 | User can search products with date filtering | `blix-scraper search kawa --active-on "this weekend"` |
| F6 | Date parsing accepts natural language | `--active-on "next Friday"`, `--valid-from "tomorrow"` |
| F7 | Invalid date inputs show helpful error | Clear error message for unparseable dates |

### Technical Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| T1 | Unit tests cover date filtering logic | Coverage > 70% for new code |
| T2 | Type hints on all new functions | mypy strict passes |
| T3 | Logging for filter operations | Structured log output |
| T4 | Backward compatibility | Existing commands work unchanged |

## Use Cases

### UC-1: Find Active Leaflets for Weekend Shopping

**Actor**: Shopper planning weekend grocery shopping  
**Scenario**:
1. User runs: `blix-scraper list-leaflets biedronka --active-on "this weekend"`
2. System parses "this weekend" to get Saturday/Sunday dates
3. System returns all leaflets valid on those dates
4. User sees which leaflets are active

**Expected Output**: List of leaflets with validity covering the weekend

### UC-2: Find Upcoming Promotions

**Actor**: User planning for next week  
**Scenario**:
1. User runs: `blix-scraper list-leaflets aldi --valid-from "next Monday"`
2. System parses "next Monday" to date
3. System returns leaflets starting from that date
4. User sees upcoming promotions

**Expected Output**: List of leaflets with valid_from >= parsed date

### UC-3: Search Products by Date

**Actor**: User looking for specific product deals  
**Scenario**:
1. User runs: `blix-scraper search kawa --active-on "this weekend"`
2. System finds all leaflets valid on the weekend
3. System searches offers within those leaflets
4. User sees coffee deals available this weekend

**Expected Output**: Search results filtered by date

### UC-4: Date Range Query

**Actor**: User compiling price comparison for a period  
**Scenario**:
1. User runs: `blix-scraper list-leaflets carrefour --within-range "2024-02-01 to 2024-02-14"`
2. System parses both dates
3. System returns leaflets with any overlap in the range
4. User gets all promotions in that two-week period

**Expected Output**: Leaflets with validity period intersecting the query range

## Technical Approach

### Dependencies

Add to `pyproject.toml`:
- `dateparser>=1.1.0` - Natural language date parsing

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Layer (Typer)                      │
│  list-leaflets, search (with date options)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Date Filtering Service                       │
│  - DateFilterService: parse dates, build predicates        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Repository Layer (Storage)                   │
│  - JSONStorage with date filtering                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Entities                            │
│  Leaflet, Offer (valid_from, valid_until)                   │
└─────────────────────────────────────────────────────────────┘
```

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Date parsing failures | Medium | Clear error messages, fallback to None |
| Performance with large datasets | Low | Filter in-memory after loading |
| Timezone handling | Medium | Use UTC as default, document behavior |
| Breaking existing commands | Low | Add optional parameters, preserve defaults |

## Timeline Estimate

- **Research**: 0.5 days - dateparser library evaluation
- **Implementation**: 2 days - CLI, filtering service, tests
- **Verification**: 0.5 days - manual testing, coverage check
- **Total**: ~3 days

## Acceptance Checklist

- [ ] New CLI options integrated with existing commands
- [ ] Date parsing handles natural language input
- [ ] Date filtering returns correct results
- [ ] Error handling for invalid dates
- [ ] Unit tests with >70% coverage
- [ ] mypy strict passes
- [ ] Documentation updated (README examples)
- [ ] Backward compatibility verified
