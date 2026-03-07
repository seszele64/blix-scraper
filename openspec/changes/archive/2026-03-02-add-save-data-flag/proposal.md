## Why

Users need the ability to persist scraped data for offline analysis, archival purposes, and integration with external tools. Currently, the scraper only displays data in the terminal via Rich tables without any option to save the results. This limits the usefulness of the tool for data analysis workflows and makes it difficult to build on top of the scraped data.

## What Changes

- Add `--save` / `-s` option to all scrape commands to save output as JSON
- Add `--output` / `-o` option to specify custom output file path
- Save scraped data (shops, leaflets, offers, search results) as JSON files
- Create a new data export capability that handles serialization and file writing
- Maintain backward compatibility - data display remains the default behavior

## Capabilities

### New Capabilities

- `data-export`: A new capability that enables saving scraped data to JSON files via CLI options. This covers:
  - Adding `--save` / `-s` flag to enable saving
  - Adding `--output` / `-o` option to specify custom file path
  - JSON serialization of all scraped entities (Shop, Leaflet, Offer, SearchResult)
  - Default file naming convention when `--output` is not specified

### Modified Capabilities

- None - this is a net-new feature that doesn't change existing requirements

## Impact

- **CLI**: New options added to `scrape_shops`, `search`, `scrape_leaflets`, `scrape_offers`, and `scrape_full_shop` commands
- **Services**: New data export utility module for JSON serialization
- **Configuration**: No changes required
- **Dependencies**: No new dependencies - standard library `json` module is sufficient

This follows the project's JSON file storage pattern as specified in the constitution.
