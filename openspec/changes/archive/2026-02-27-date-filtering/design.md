# Technical Design: Date Filtering Feature

**Parent Change**: date-filtering  
**Status**: Draft

## Architecture Overview

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         User (CLI)                                 │
│  blix-scraper list-leaflets --active-on "this weekend"           │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                    CLI Layer (Typer)                               │
│  - src/cli/__init__.py                                            │
│  - New options: --active-on, --valid-from, --valid-until,        │
│    --within-range                                                 │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│              Date Parsing Service                                  │
│  - src/utils/date_parser.py                                        │
│  - Converts string input to datetime                              │
│  - Uses dateparser library for natural language                   │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│              Date Filter Options (Domain)                          │
│  - src/domain/date_filter.py                                      │
│  - DateFilterOptions model                                         │
│  - Predicate builders                                              │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│           Repository/Storage Layer                                  │
│  - src/storage/date_filtered_storage.py                           │
│  - Filtered load methods                                           │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│               Domain Entities                                       │
│  - src/domain/entities.py                                         │
│  - Leaflet.is_valid_on(), is_valid_in_range()                     │
│  - Offer.is_valid_on(), is_valid_in_range()                       │
└────────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### Sequence Diagram: List Leaflets with Date Filter

```
┌─────────┐     ┌──────────┐     ┌────────────┐     ┌──────────────┐     ┌─────────┐
│  User   │     │   CLI    │     │DateParser  │     │DateFilter    │     │ Storage │
└────┬────┘     └────┬─────┘     └──────┬─────┘     └──────┬───────┘     └────┬────┘
     │               │                  │                   │                  │
     │list-leaflets  │                  │                   │                  │
     │--active-on   │                  │                   │                  │
     │"this weekend"│                  │                   │                  │
     │──────────────>│                  │                   │                  │
     │               │                  │                   │                  │
     │               │parse("this       │                   │                  │
     │               │weekend")         │                   │                  │
     │               │─────────────────>│                   │                  │
     │               │                  │                   │                  │
     │               │<─────────────────│                   │                  │
     │               │(Sat, Sun dates)  │                   │                  │
     │               │                  │                   │                  │
     │               │                  │Create filter      │                  │
     │               │                  │───> DateFilterOptions  │
     │               │                  │                   │──────┐          │
     │               │                  │                   │      │          │
     │               │                  │                   │<─────┘          │
     │               │                  │                   │                  │
     │               │                  │                   │load_all(filter) │
     │               │                  │                   │─────────────────>│
     │               │                  │                   │                  │
     │               │                  │                   │                  │
     │               │                  │                   │<─────────────────│
     │               │                  │                   │(filtered list)  │
     │               │                  │                   │                  │
     │               │Display results   │                   │                  │
     │<──────────────│                  │                   │                  │
     │               │                  │                   │                  │
```

## Date Filtering Algorithm

### Core Filter Logic

```python
def apply_date_filter(
    entities: List[Leaflet],
    filter_options: DateFilterOptions
) -> List[Leaflet]:
    """Apply date filter to list of entities.
    
    Args:
        entities: List of Leaflet entities
        filter_options: Date filtering options
        
    Returns:
        Filtered list of entities
    """
    # If no filter, return all
    if not filter_options.has_date_filter():
        return entities
    
    result = entities
    
    # Apply active_on filter
    if filter_options.active_on is not None:
        result = [
            e for e in result 
            if e.is_valid_on(filter_options.active_on)
        ]
    
    # Apply valid_from filter
    if filter_options.valid_from is not None:
        result = [
            e for e in result
            if e.valid_from >= filter_options.valid_from
        ]
    
    # Apply valid_until filter
    if filter_options.valid_until is not None:
        result = [
            e for e in result
            if e.valid_until <= filter_options.valid_until
        ]
    
    # Apply range filter (date_from/date_to)
    if filter_options.date_from is not None and filter_options.date_to is not None:
        result = [
            e for e in result
            if e.is_valid_in_range(
                filter_options.date_from, 
                filter_options.date_to
            )
        ]
    
    return result
```

### Range Overlap Detection

```python
def has_date_overlap(
    entity_start: datetime,
    entity_end: datetime,
    query_start: datetime,
    query_end: datetime
) -> bool:
    """Check if entity validity overlaps with query range.
    
    Returns True if there is any overlap between:
    - [entity_start, entity_end] (entity validity period)
    - [query_start, query_end] (query range)
    
    Overlap exists if:
      entity_start <= query_end AND entity_end >= query_start
    """
    return entity_start <= query_end and entity_end >= query_start
```

## CLI Command Structure

### Modified Commands

#### list-leaflets Command

```python
@app.command("list-leaflets")
def list_leaflets(
    shop: str = typer.Argument(..., help="Shop slug"),
    active_only: bool = typer.Option(False, "--active-only"),
    active_on: str = typer.Option(None, "--active-on", "-a"),
    valid_from: str = typer.Option(None, "--valid-from", "-f"),
    valid_until: str = typer.Option(None, "--valid-until", "-u"),
    within_range: str = typer.Option(None, "--within-range", "-r"),
) -> None:
    """List leaflets with optional date filtering."""
    
    # Parse date inputs
    date_filter = DateFilterOptions()
    
    if active_on:
        date_filter.active_on = DateParser.parse(active_on)
    
    if valid_from:
        date_filter.valid_from = DateParser.parse(valid_from)
    
    if valid_until:
        date_filter.valid_until = DateParser.parse(valid_until)
    
    if within_range:
        date_from, date_to = DateParser.parse_range(within_range)
        date_filter.date_from = date_from
        date_filter.date_to = date_to
    
    # Load with filter
    storage = DateFilteredJSONStorage(shop_dir, Leaflet)
    leaflets = storage.load_all(date_filter)
    
    # Display...
```

### New Files Structure

```
src/
├── domain/
│   ├── entities.py          # Existing: Leaflet, Offer
│   └── date_filter.py       # NEW: DateFilterOptions, predicates
├── storage/
│   ├── json_storage.py      # Existing: JSONStorage
│   └── date_filtered_storage.py  # NEW: DateFilteredJSONStorage
├── utils/
│   └── date_parser.py       # NEW: DateParser, DateParseError
└── cli/
    └── __init__.py          # MODIFIED: Add date options

tests/
├── domain/
│   └── test_date_filter.py  # NEW
├── storage/
│   └── test_date_filtered_storage.py  # NEW
├── utils/
│   └── test_date_parser.py  # NEW
└── fixtures/
    └── leaflets/
        └── ...
```

## Data Models

### DateFilterOptions

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Callable, TypeVar

T = TypeVar('T')

class DateFilterOptions(BaseModel):
    """Options for filtering by date."""
    
    active_on: Optional[datetime] = Field(
        default=None,
        description="Filter to entities valid on this specific date"
    )
    valid_from: Optional[datetime] = Field(
        default=None,
        description="Filter to entities valid from this date onwards"
    )
    valid_until: Optional[datetime] = Field(
        default=None,
        description="Filter to entities valid until this date"
    )
    date_from: Optional[datetime] = Field(
        default=None,
        alias="range-start",
        description="Start of date range"
    )
    date_to: Optional[datetime] = Field(
        default=None,
        alias="range-end",
        description="End of date range"
    )
    
    def has_date_filter(self) -> bool:
        """Check if any date filter is active."""
        return any([
            self.active_on is not None,
            self.valid_from is not None,
            self.valid_until is not None,
            self.date_from is not None,
            self.date_to is not None,
        ])
    
    def to_predicate(self) -> Callable[[T], bool]:
        """Convert to predicate function."""
        # Returns filter function for entities
        ...
```

## Testing Approach

### Unit Tests

#### Date Filter Tests

```python
# tests/domain/test_date_filter.py

import pytest
from datetime import datetime, timezone
from src.domain.date_filter import DateFilterOptions
from src.domain.entities import Leaflet, LeafletStatus

class TestDateFilterOptions:
    
    def test_has_date_filter_with_active_on(self):
        filter = DateFilterOptions(
            active_on=datetime(2024, 1, 20, tzinfo=timezone.utc)
        )
        assert filter.has_date_filter() is True
    
    def test_has_date_filter_empty(self):
        filter = DateFilterOptions()
        assert filter.has_date_filter() is False
    
    def test_to_predicate_active_on(self):
        filter = DateFilterOptions(
            active_on=datetime(2024, 1, 20, tzinfo=timezone.utc)
        )
        predicate = filter.to_predicate()
        
        # Leaflet valid on that date
        leaflet = Leaflet(
            leaflet_id=1,
            shop_slug="test",
            name="Test",
            cover_image_url="https://example.com/img.jpg",
            url="https://example.com/1",
            valid_from=datetime(2024, 1, 15, tzinfo=timezone.utc),
            valid_until=datetime(2024, 1, 25, tzinfo=timezone.utc),
            status=LeafletStatus.ACTIVE,
        )
        assert predicate(leaflet) is True
```

#### Date Parser Tests

```python
# tests/utils/test_date_parser.py

import pytest
from datetime import datetime, timezone
from src.utils.date_parser import DateParser, DateParseError

class TestDateParser:
    
    def test_parse_iso_date(self):
        result = DateParser.parse("2024-01-20")
        assert result == datetime(2024, 1, 20, tzinfo=timezone.utc)
    
    def test_parse_natural_today(self):
        result = DateParser.parse("today")
        expected = datetime.now(timezone.utc).date()
        assert result.date() == expected
    
    def test_parse_invalid_raises_error(self):
        with pytest.raises(DateParseError):
            DateParser.parse("not-a-date")
    
    def test_parse_range(self):
        start, end = DateParser.parse_range("2024-01-01 to 2024-01-31")
        assert start == datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert end == datetime(2024, 1, 31, tzinfo=timezone.utc)
```

### Integration Tests

```python
# tests/cli/test_date_filtering.py

import pytest
from typer.testing import CliRunner
from src.cli import app

runner = CliRunner()

class TestListLeafletsDateFilter:
    
    def test_list_leaflets_active_on(self, tmp_path, monkeypatch):
        # Setup test data
        ...
        
        result = runner.invoke(
            app, 
            ["list-leaflets", "biedronka", "--active-on", "2024-01-20"]
        )
        
        assert result.exit_code == 0
        assert "filtered by: active-on" in result.stdout
    
    def test_invalid_date_shows_error(self):
        result = runner.invoke(
            app,
            ["list-leaflets", "biedronka", "--active-on", "not-a-date"]
        )
        
        assert result.exit_code != 0
        assert "Could not parse" in result.stdout
```

### Test Fixtures

Create test fixtures in `tests/fixtures/leaflets/`:

```json
// tests/fixtures/leaflets/biedronka_1234.json
{
  "leaflet_id": 1234,
  "shop_slug": "biedronka",
  "name": "Promocje weekendowe",
  "cover_image_url": "https://example.com/cover.jpg",
  "url": "https://blix.pl/biedronka/1234",
  "valid_from": "2024-01-19T00:00:00Z",
  "valid_until": "2024-01-21T23:59:59Z",
  "status": "active",
  "page_count": 4,
  "scraped_at": "2024-01-15T10:00:00Z"
}
```

## Error Handling

### Date Parse Errors

```python
try:
    parsed_date = DateParser.parse(date_string)
except DateParseError as e:
    raise typer.BadParameter(
        f"Could not parse date '{date_string}'. "
        f"Please use a valid format like '2024-01-20' "
        f"or natural language like 'tomorrow', 'next Friday'."
    )
```

### Empty Results

```python
if not leaflets:
    console.print(
        f"[yellow]No leaflets found"
        f"{filter_description}[/yellow]"
    )
    return
```

## Logging

```python
import structlog

logger = structlog.get_logger(__name__)

def apply_date_filter(entities, filter_options):
    logger.info(
        "applying_date_filter",
        entity_count=len(entities),
        active_on=filter_options.active_on,
        valid_from=filter_options.valid_from,
        valid_until=filter_options.valid_until,
        range_start=filter_options.date_from,
        range_end=filter_options.date_to,
    )
    
    result = _do_filter(entities, filter_options)
    
    logger.info(
        "date_filter_complete",
        input_count=len(entities),
        output_count=len(result),
    )
    
    return result
```

## Performance Considerations

1. **In-Memory Filtering**: Current approach loads all data then filters in memory
2. **Lazy Loading**: Could be added later for large datasets
3. **Caching**: Could cache parsed dates for repeated queries
4. **Indexing**: Future optimization: pre-compute date indexes

## Backward Compatibility

- All existing CLI options preserved
- New options default to None (no filtering)
- Storage `load_all()` works without filter parameter
- No breaking changes to existing functionality
