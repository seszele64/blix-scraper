# Repository Layer Date Filtering Specification

**Spec ID**: 02-repository-filtering  
**Parent Change**: date-filtering  
**Status**: Draft

## Overview

This specification defines how date filtering is implemented in the repository layer. The repository layer handles data persistence and retrieval. Date filtering should be applied when loading entities from storage.

## ADDED Requirements

### Requirement: Date Filtered Load

The repository layer MUST support loading entities with date filtering applied.

#### Scenario: Load all leaflets with active_on filter
- **WHEN** loading with date_filter active_on="2024-01-20" (5 Leaflet entities in storage, 3 valid on "2024-01-20")
- **THEN** the result contains only 3 leaflets

#### Scenario: Load all leaflets with valid_from filter
- **WHEN** loading with date_filter valid_from="2024-01-15" (Leaflet entities with valid_from dates of 2024-01-01, 2024-01-15, 2024-01-25)
- **THEN** the result contains 2 leaflets (2024-01-15 and 2024-01-25)

#### Scenario: Load with no filter returns all
- **WHEN** loading with no date_filter (10 Leaflet entities in storage)
- **THEN** the result contains all 10 leaflets

### Requirement: Filtered Count

The repository layer MUST provide count methods with filtering.

#### Scenario: Count filtered entities
- **WHEN** calling count with active_on="2024-01-20" (10 Leaflet entities, 4 valid on "2024-01-20")
- **THEN** the result is 4

#### Scenario: Count by shop with filter
- **WHEN** calling count_by_shop with shop="biedronka" and active_on="2024-01-20" (5 leaflets for shop "biedronka", 2 valid on "2024-01-20")
- **THEN** the result is 2

#### Scenario: Count with no filter returns total
- **WHEN** calling count with no filter (15 Leaflet entities)
- **THEN** the result is 15

### Requirement: Filter Entity by Date Range

The system MUST provide utility to filter a list of entities by date.

#### Scenario: Filter leaflet list by date range
- **WHEN** filtering with date_from="2024-01-01" and date_to="2024-01-31" (a list of Leaflets with various validity dates)
- **THEN** only leaflets with any overlap in that range are returned

#### Scenario: Filter returns empty for no matches
- **WHEN** filtering with date_from="2024-01-01" to "2024-01-31" (Leaflets all valid in March 2024)
- **THEN** the result is an empty list

#### Scenario: Combined date filter criteria
- **WHEN** applying to a list of entities (a DateFilter with date_from and date_to set)
- **THEN** both criteria must match (AND logic)

### Requirement: Filtered Load for Shops

The repository MUST support filtered loads across all shops.

#### Scenario: Get shops with active leaflets on date
- **WHEN** calling get_shops_with_active_leaflets("2024-01-20") (shops "biedronka", "carrefour", "lidl" with various leaflet dates)
- **THEN** only shops with leaflets valid on that date are returned

#### Scenario: Load all shops with filtered leaflet counts
- **WHEN** calling load_all_shops with active_on filter (shops with varying numbers of valid leaflets)
- **THEN** each shop's leaflet count reflects filtered results

### Requirement: Offer Filtering by Leaflet Dates

The system MUST support filtering offers based on their associated leaflet's validity dates.

#### Scenario: Filter offers by parent leaflet dates
- **WHEN** filtering offers by leaflet dates with active_on="2024-01-20" (offers linked to leaflets with different validity periods)
- **THEN** only offers from leaflets valid on that date are returned

#### Scenario: Offers inherit leaflet validity
- **WHEN** filtering by leaflet dates (an Offer with no explicit dates but linked to Leaflet)
- **THEN** the offer is included if its parent leaflet matches the filter

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CLI Input    │────▶│  Date Filter    │────▶│  JSONStorage   │
│                 │     │   Options        │     │  load_all()    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                  ┌─────────────────┐
                                                  │  In-Memory      │
                                                  │  Filter         │
                                                  └─────────────────┘
```

## Filter Logic

### Leaflet Filtering

```python
def leaflet_matches_filter(leaflet: Leaflet, filter: DateFilterOptions) -> bool:
    """Check if leaflet matches date filter."""
    
    # active_on: Check if date falls within validity period
    if filter.active_on is not None:
        if not leaflet.is_valid_on(filter.active_on):
            return False
    
    # valid_from: Check if leaflet starts on or after this date
    if filter.valid_from is not None:
        if leaflet.valid_from < filter.valid_from:
            return False
    
    # valid_until: Check if leaflet ends on or before this date
    if filter.valid_until is not None:
        if leaflet.valid_until > filter.valid_until:
            return False
    
    # date_from/date_to: Range check (overlap)
    if filter.date_from is not None and filter.date_to is not None:
        # Check for any overlap
        if leaflet.valid_until < filter.date_from:
            return False
        if leaflet.valid_from > filter.date_to:
            return False
    
    return True
```

### Offer Filtering

```python
def offer_matches_filter(offer: Offer, filter: DateFilterOptions) -> bool:
    """Check if offer matches date filter.
    
    Note: Offers have their own valid_from/valid_until fields.
    """
    # Same logic as leaflet, but using offer's date fields
    ...
```

## File Locations

- New storage module: `src/storage/date_filtered_storage.py`
- Tests: `tests/storage/test_date_filtered_storage.py`

## Edge Cases

| Edge Case | Expected Behavior |
|-----------|------------------|
| Empty entity list | Return empty list |
| No matching entities | Return empty list |
| Filter with no criteria | Return all entities |
| Invalid date (None) | Skip that filter criteria |
| Single date in range query | Treat as point-in-time query |

## Performance Considerations

- Filtering is done in-memory after loading all files
- For large datasets, consider lazy loading or pagination
- Logging of filter operations for debugging

## Integration with Existing Code

The new storage class should extend or wrap `JSONStorage`:

```python
class DateFilteredJSONStorage(JSONStorage[T]):
    """JSONStorage with date filtering support."""
    
    def __init__(self, base_dir: Path, entity_type: type[T]) -> None:
        super().__init__(base_dir, entity_type)
    
    def load_all(
        self, 
        date_filter: Optional[DateFilterOptions] = None
    ) -> List[T]:
        entities = super().load_all()
        
        if date_filter and date_filter.has_date_filter():
            return filter_by_date(entities, date_filter)
        
        return entities
```

This maintains backward compatibility while adding filtering capabilities.
