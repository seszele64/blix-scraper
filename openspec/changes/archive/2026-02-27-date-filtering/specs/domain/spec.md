# Domain Layer Date Filtering Specification

**Spec ID**: 01-domain-filtering  
**Parent Change**: date-filtering  
**Status**: Draft

## Overview

This specification defines the domain layer requirements for date filtering capabilities in the blix-scraper project. The domain layer already contains `valid_from` and `valid_until` fields on `Leaflet` and `Offer` entities. This spec defines how date filtering should work at the domain level.

## ADDED Requirements

### Requirement: Date Validity Check
The system MUST provide methods to check if an entity is valid on a specific date.

#### Scenario: Leaflet valid on specific date
- **WHEN** checking if the leaflet is valid on "2024-01-20"
- **THEN** the result should be True

#### Scenario: Leaflet not valid on date outside range
- **WHEN** checking if the leaflet is valid on "2024-01-22"
- **THEN** the result should be False

#### Scenario: Leaflet valid on boundary date
- **WHEN** checking if the leaflet is valid on "2024-01-19"
- **THEN** the result should be True

#### Scenario: Offer valid on specific date
- **WHEN** checking if the offer is valid on "2024-01-20"
- **THEN** the result should be True

### Requirement: Date Range Validity Check

The system MUST provide methods to check if an entity is valid within a date range.

#### Scenario: Leaflet valid in overlapping range
- **WHEN** checking if valid in range "2024-01-20" to "2024-01-30" (a Leaflet with valid_from="2024-01-15" and valid_until="2024-01-25")
- **THEN** the result should be True

#### Scenario: Leaflet not valid in non-overlapping range
- **WHEN** checking if valid in range "2024-01-25" to "2024-01-30" (a Leaflet with valid_from="2024-01-15" and valid_until="2024-01-20")
- **THEN** the result should be False

#### Scenario: Leaflet partially overlaps range
Given a Leaflet with valid_from="2024-01-10" and valid_until="2024-01-15"
 in range "2024-01-12" to "When checking if valid2024-01-20"
Then the result should be True

### Requirement: Date Filter Predicate

The system MUST provide filter predicates for use with repository layer.

#### Scenario: Create leaflet predicate for active_on
- **WHEN** converting to Leaflet predicate (a DateFilter with active_on="2024-01-20")
- **THEN** the predicate returns True for leaflets valid on that date

#### Scenario: Create offer predicate for valid_from
- **WHEN** converting to Offer predicate (a DateFilter with valid_from="2024-01-15")
- **THEN** the predicate returns True for offers with valid_from >= 2024-01-15

### Requirement: Date Filter Builder

The system MUST provide a builder/factory for creating date filters from user input.

#### Scenario: Build filter for specific date
- **WHEN** creating DateFilter using active_on builder (date "2024-01-20")
- **THEN** the DateFilter has active_on set to that date

#### Scenario: Build filter for date range
- **WHEN** creating DateFilter using from_range builder (start_date "2024-01-01" and end_date "2024-01-31")
- **THEN** the DateFilter has date_from and date_to set

### Requirement: Filter Combination

The system MUST support combining date filters.

#### Scenario: Combine active_on with valid_from
- **WHEN** applying filter to leaflets (DateFilter with active_on="2024-01-20" and valid_from="2024-01-01")
- **THEN** only leaflets valid on 2024-01-20 AND starting from 2024-01-01 are returned

#### Scenario: All filter criteria must match
- **WHEN** applying filter (DateFilter with active_on, valid_from, and valid_until all set)
- **THEN** leaflet must satisfy all three conditions

## Data Flow

```
User Input (CLI)
       │
       ▼
Date Parsing Service (dateparser)
       │
       ▼
DateFilter (domain model)
       │
       ▼
Predicate Functions
       │
       ▼
Filtered Results
```

## Type Definitions

### DateFilterOptions

```python
from typing import Optional
from datetime import datetime

class DateFilterOptions(BaseModel):
    """Options for date filtering."""
    
    active_on: Optional[datetime] = Field(
        None, 
        description="Filter to entities valid on this date"
    )
    valid_from: Optional[datetime] = Field(
        None,
        description="Filter to entities valid from this date onwards"
    )
    valid_until: Optional[datetime] = Field(
        None,
        description="Filter to entities valid until this date"
    )
    date_from: Optional[datetime] = Field(
        None,
        alias="within-range-start",
        description="Start of date range (used with --within-range)"
    )
    date_to: Optional[datetime] = Field(
        None,
        alias="within-range-end", 
        description="End of date range (used with --within-range)"
    )
    
    def has_date_filter(self) -> bool:
        """Check if any date filter is applied."""
        return any([
            self.active_on is not None,
            self.valid_from is not None,
            self.valid_until is not None,
            self.date_from is not None,
            self.date_to is not None,
        ])
    
    def to_predicate(self) -> Callable[[T], bool]:
        """Convert to predicate for filtering."""
        ...
```

## File Locations

- Domain entities: `src/domain/entities.py`
- Date filter models: `src/domain/date_filter.py` (new file)
- Tests: `tests/domain/test_date_filter.py` (new file)

## Dependencies

- No new dependencies at domain layer
- Uses existing `datetime` from stdlib
- Uses `pydantic` for `DateFilterOptions` model
