## Context

The blix-scraper currently exports all available fields for each entity type (Shop, Leaflet, Offer, SearchResult). Users have expressed the need to filter which fields are included in the output to reduce file sizes and simplify downstream processing. This design addresses implementing field filtering at the export layer without modifying the scraping logic.

## Current State

- All entity fields are exported via `model_dump(mode="json")` in `src/cli/__init__.py`
- Data export handled by `src/utils/data_export.py`
- Field metadata tracked in `get_entity_fields()` function
- No existing field filtering capability

## Goals / Non-Goals

**Goals:**
- Add CLI options to specify which fields to include or exclude when saving data
- Support field filtering for all entity types (Shop, Leaflet, Offer, SearchResult)
- Maintain backward compatibility - all existing commands work without changes
- Provide clear error messages for invalid field names

**Non-Goals:**
- Modifying scraper logic to skip fetching certain fields (all fields still fetched from the website)
- Adding field filtering at the database/storage layer (only affects JSON export)
- Supporting field aliases or renaming (only include/exclude)
- Adding new export formats (JSON only for now)

## Decisions

### 1. CLI Option Design

**Decision:** Use `--fields` for inclusion and `--exclude` for exclusion, both accepting comma-separated values.

**Rationale:**
- Clear distinction between "only these fields" vs "all except these fields"
- Follows common CLI conventions (e.g., git, docker)
- Allows combining both (e.g., all fields except images)

**Order of Operations:** Exclude is applied after include. This means:
1. First, include only the specified fields (if `--fields` is provided)
2. Then, remove any fields from the exclude list (if `--exclude` is provided)

Example: `--fields name,price --exclude price` will result in only `name` being included (price is excluded after include).

**Alternative considered:** Single `--fields` with prefixes (`+field,-field`). Rejected because it's harder to parse and document.

### 2. Field Validation Strategy

**Decision:** Validate field names against entity schemas at CLI parsing time, before any scraping occurs.

**Rationale:**
- Fail fast with clear error message
- Prevents wasting time scraping only to fail at export
- Use Pydantic model fields for validation (already defined in entities)

**Alternative considered:** Validate at export time. Rejected - poor UX to scrape and then fail.

### 3. Nested Field Handling

**Decision:** Flat field namespace only (e.g., `name`, `price`), no nested field support (e.g., `leaflet.name`).

**Rationale:**
- Simpler implementation and user experience
- Most common use cases need flat fields
- Can extend later if needed

**Alternative considered:** Support dot notation for nested fields. Deferred to future enhancement.

### 4. Default Field Set

**Decision:** Include all fields by default (no filtering applied).

**Rationale:**
- Backward compatible - existing scripts continue to work
- Users explicitly opt-in to filtering
- No surprise behavior changes

### 5. Implementation Location

**Decision:** Implement field filtering in the export layer (`src/utils/data_export.py`), not in entity classes.

**Rationale:**
- Separation of concerns - entities remain pure
- Reusable across different commands
- Easier to test and maintain

### 6. Nested Data Filtering for scrape_full_shop

**Decision:** Field filtering applies uniformly to all nested objects (shop, leaflets, offers) when using `scrape_full_shop`.

**Rationale:**
- Consistent behavior across all data levels
- Users can filter at any level uniformly
- Simplifies CLI interface - single set of fields/exclude params applies to entire output

**Implementation:** When filtering is applied to nested data:
- If `--fields` is specified, only those fields are included in each nested object
- If `--exclude` is specified, those fields are removed from each nested object
- The same field names apply across all entity types (e.g., `name` filters shop.name, leaflet.name, and offer.name if present)

**Example:**
```bash
blix-scraper scrape_full_shop biedronka --fields name,price --save
# Output: shop with only name, leaflets with only name, offers with only name,price
```

## Architecture

```
CLI Commands (scrape_shops, search, etc.)
    │
    ▼
┌─────────────────────────────────────┐
│  _export_data()                    │
│  - Accepts fields/exclude params   │
│  - Validates field names           │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Field Filter Function             │
│  - Filters dict based on fields    │
│  - Handles include/exclude logic  │
└─────────────────────────────────────┘
    │
    ▼
save_to_json()
```

## Data Model Changes

### New Parameters to `_export_data()`

```python
def _export_data(
    # ... existing params ...
    fields: list[str] | None = None,    # Fields to include
    exclude: list[str] | None = None,  # Fields to exclude
) -> Path | None
```

### New Utility Functions

```python
def get_available_fields(entity_type: str) -> list[str]:
    """Get list of available fields for an entity type."""
    
def validate_fields(entity_type: str, fields: list[str]) -> list[str]:
    """Validate field names against entity schema. Returns valid fields or raises ValueError."""

def filter_fields(data: dict | list[dict], fields: list[str] | None, exclude: list[str] | None) -> dict | list[dict]:
    """Filter fields from data based on include/exclude lists."""
```

## Field Discovery Strategy

**Approach:** Use Pydantic model introspection to dynamically discover available fields from entity classes.

**Implementation:**
- Import entity classes from `src.domain.entities`
- Use `model_fields` attribute to get field names and types
- Cache field metadata at module level for performance
- Support all entity types: Shop, Leaflet, Offer, SearchResult

**Benefits:**
- Single source of truth - field definitions live in entity classes
- No manual maintenance of field lists
- Automatic updates when entities are modified
- Strong type safety through Pydantic

**Implementation Pattern:**

```python
from typing import Any
from pydantic import BaseModel
from src.domain.entities import Shop, Leaflet, Offer, SearchResult

ENTITY_MODELS: dict[str, type[BaseModel]] = {
    "shop": Shop,
    "leaflet": Leaflet,
    "offer": Offer,
    "search_result": SearchResult,
}

def get_available_fields(entity_type: str) -> list[str]:
    """Get field names from Pydantic model."""
    model = ENTITY_MODELS.get(entity_type)
    if model is None:
        msg = f"Unknown entity type: {entity_type}"
        raise ValueError(msg)
    return list(model.model_fields.keys())
```

## Field Lists by Entity Type

### Shop Fields
- slug, brand_id, name, logo_url, category, leaflet_count, is_popular, scraped_at

### Leaflet Fields
- leaflet_id, shop_slug, name, cover_image_url, url, valid_from, valid_until, status, page_count, scraped_at

### Offer Fields
- leaflet_id, name, price, image_url, page_number, position_x, position_y, width, height, valid_from, valid_until, scraped_at

### SearchResult Fields
- hash, name, image_url, manufacturer_name, manufacturer_uuid, brand_name, brand_uuid, sub_brand_name, sub_brand_uuid, hiper_category_id, offer_subcategory_id, product_leaflet_page_uuid, leaflet_id, page_number, price, percent_discount, valid_from, valid_until, position_x, position_y, width, height, search_query, scraped_at, shop_name

## Risks / Trade-offs

1. **[Risk]** Users might confuse field names with entity property names
   - **Mitigation:** Add `--fields-list` option to show available fields; provide helpful error messages with suggestions

2. **[Risk]** Adding fields parameter to all CLI commands is repetitive
   - **Mitigation:** Create a shared Typer callback for field validation that can be reused

3. **[Risk]** Backward compatibility if field names change in entities
   - **Mitigation:** Use entity field metadata dynamically from Pydantic models; validate at runtime

4. **[Risk]** Empty field list results in no data
   - **Mitigation:** Warn user if resulting data would be empty; allow at least one field

## Migration Plan

1. **Phase 1**: Add utility functions in `src/utils/data_export.py`
2. **Phase 2**: Add `--fields`, `--exclude`, and `--fields-list` options to CLI
3. **Phase 3**: Wire up field filtering in `_export_data()` function
4. **Phase 4**: Add tests for field filtering functionality
5. **Phase 5**: Update documentation

**Rollback:** Simply remove the new CLI options - all existing scripts continue to work.

## Open Questions

1. Should we support predefined field groups (e.g., `--fields basic`, `--fields full`)?
   - **Decision:** OUT OF SCOPE for v1 - can add later if users request it

2. Should field filtering apply to metadata in JSON export?
   - **Decision:** No - metadata should always include fields used for debugging

3. Should we cache field validation results?
   - **Decision:** Not needed - validation is fast and happens once per command

(End of file - total 220 lines)
