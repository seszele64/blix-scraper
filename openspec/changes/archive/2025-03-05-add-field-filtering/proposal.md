## Why

Users currently receive all available fields when scraping data from blix.pl, even when they only need a subset of fields (e.g., just name, price, and shop_name). This creates unnecessary data transfer, larger storage files, and makes downstream processing more complex. Adding field filtering will give users control over which fields to fetch and save, reducing data volume and improving usability.

## What Changes

- Add CLI option `--fields` to specify which entity fields to include in output
- Modify data export layer to filter fields before saving to JSON
- Add validation for field names against entity schemas
- Support both explicit field lists and predefined field groups
- Add help text showing available fields for each entity type

### New CLI Options

- `--fields`: Comma-separated list of fields to include (e.g., `--fields name,price,shop_name`)
- `--fields-list`: Show available fields for the entity without running scraper
- Support `--exclude` option to omit specific fields

## Capabilities

### New Capabilities

- `field-filtering`: Allow users to specify which fields to include/exclude when exporting scraped data. This applies to all entity types (Shop, Leaflet, Offer, SearchResult) and works with all save commands.

### Modified Capabilities

None. This is a new capability that doesn't change existing behavior - it only adds optional filtering.

## Impact

- **CLI**: Add new options to all save-enabled commands (scrape_shops, search, scrape_leaflets, scrape_offers, scrape_full_shop)
- **Services**: Update export functions to accept field filtering parameters
- **Utils**: Modify data_export utilities to support field filtering
- **Documentation**: Update CLI help and developer guide with field filtering usage
- **scrape_full_shop**: Special handling needed for nested data (shop → leaflets → offers) - filtering applies uniformly to all nested objects
- **No breaking changes**: All existing functionality preserved; field filtering is purely additive

## User Stories

1. As a user, I want to specify only the fields I need so I can reduce file sizes
2. As a data analyst, I want to get just name and price fields so I can quickly import into spreadsheets
3. As a developer, I want to exclude large fields like image_url when testing
4. As a user, I want to see available fields before running a scrape

## Examples

```bash
# Get only name and price from search
blix-scraper search "kawa" --fields name,price --save

# Get offers with basic info only
blix-scraper scrape_offers biedronka 123 --fields name,price,shop_name --save

# Exclude large image fields
blix-scraper scrape_shops --exclude image_url --save

# List available fields
blix-scraper search --fields-list
```
