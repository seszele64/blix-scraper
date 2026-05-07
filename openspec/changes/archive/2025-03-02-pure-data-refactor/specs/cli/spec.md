# CLI Command Specifications

**Spec ID**: 02-cli  
**Parent Change**: pure-data-refactor  
**Status**: Draft

## Overview

This specification defines the CLI command changes required for the pure-data refactor. The CLI must fetch data on-demand without reading from saved files.

## ADDED Requirements

### Requirement: scrape-shops On-Demand Display

The scrape-shops command SHALL fetch shops on-demand and display them without saving.

#### Scenario: Scrape and display shops
- **GIVEN** the user runs `blix-scraper scrape-shops --headless`
- **WHEN** the command executes
- **THEN** it creates a ScraperService and calls get_shops()
- **AND** displays a table of shops directly
- **AND** no files are saved to data/ directory

#### Scenario: Display format for shops
- **GIVEN** scrape-shops command successfully fetches shops
- **WHEN** the results are displayed
- **THEN** a table shows: Slug, Name, Leaflets count, Popular indicator

### Requirement: scrape-leaflets On-Demand Display

The scrape-leaflets command SHALL fetch leaflets on-demand and display them without saving.

#### Scenario: Scrape and display leaflets
- **GIVEN** the user runs `blix-scraper scrape-leaflets biedronka --headless`
- **WHEN** the command executes
- **THEN** it creates a ScraperService and calls get_leaflets("biedronka")
- **AND** displays a table of leaflets directly
- **AND** no files are saved to data/ directory

#### Scenario: Display format for leaflets
- **GIVEN** scrape-leaflets command successfully fetches leaflets
- **WHEN** the results are displayed
- **THEN** a table shows: ID, Name, Status, Valid From, Valid Until

### Requirement: scrape-offers On-Demand Display

The scrape-offers command SHALL fetch offers on-demand and display them without saving.

#### Scenario: Scrape and display offers
- **GIVEN** the user runs `blix-scraper scrape-offers biedronka 12345 --headless`
- **WHEN** the command executes
- **THEN** it creates a ScraperService and calls get_offers()
- **AND** displays sample offers
- **AND** no files are saved to data/ directory

### Requirement: search On-Demand with Date Filtering

The search command SHALL fetch results on-demand with in-memory date filtering without saved leaflets.

#### Scenario: Search with date filter
- **GIVEN** the user runs `blix-scraper search kawa --active-on "this weekend" --headless`
- **WHEN** the command executes
- **THEN** it creates a ScraperService and calls search() with date_filter
- **AND** date filtering happens in-memory after scraping
- **AND** no files are saved to data/ directory

#### Scenario: Search combines multiple date filters
- **GIVEN** the user runs `blix-scraper search kawa --valid-from "next Monday" --valid-until "end of month" --headless`
- **WHEN** the command executes
- **THEN** the date_filter includes both valid_from and valid_until
- **AND** results are filtered in-memory to only show products in leaflets valid during that period

#### Scenario: Search shows statistics
- **GIVEN** search command returns results
- **WHEN** results are displayed
- **THEN** statistics are shown: total results, results with price, cheapest/most expensive/average price, unique brands

## MODIFIED Requirements

### Requirement: list-shops Command Removed

The list-shops command SHALL be removed entirely.

#### Scenario: Command no longer available
- **GIVEN** the user runs `blix-scraper list-shops`
- **WHEN** the command executes
- **THEN** a "command not found" error is returned
- **AND** the CLI does not attempt to read from data/shops/shops.json

### Requirement: list-leaflets Command Removed

The list-leaflets command SHALL be removed entirely.

#### Scenario: Command no longer available
- **GIVEN** the user runs `blix-scraper list-leaflets biedronka`
- **WHEN** the command executes
- **THEN** a "command not found" error is returned
- **AND** the CLI does not attempt to read from data/leaflets/

### Requirement: CLI No Storage Imports

CLI SHALL NOT import from storage module.

#### Scenario: No storage module imports
- **GIVEN** the CLI module src/cli/__init__.py
- **WHEN** imports are analyzed
- **THEN** there are no imports from src.storage or any storage-related modules

#### Scenario: No JSONStorage usage
- **GIVEN** the CLI module
- **WHEN** the code is analyzed
- **THEN** there is no usage of JSONStorage class

### Requirement: CLI No Data Directory Reading

CLI SHALL NOT read from data/ directory.

#### Scenario: No data file reads
- **GIVEN** any CLI command executes
- **WHEN** file system operations are monitored
- **THEN** no reads occur in the data/ directory
- **AND** no JSON files are loaded

### Requirement: All Commands Use ScraperService

All scraping commands SHALL use ScraperService instead of ScraperOrchestrator.

#### Scenario: Migrate scrape-shops to ScraperService
- **GIVEN** scrape-shops command is executed
- **WHEN** it runs
- **THEN** it uses ScraperService for scraping
- **AND** NOT ScraperOrchestrator

#### Scenario: Migrate all scraping commands
- **GIVEN** any scraping command is executed
- **WHEN** it runs
- **THEN** it uses ScraperService for all scraping operations

## REMOVED Requirements

### Requirement: Offline Mode Commands

The offline mode commands that read from saved files SHALL be removed.

#### Scenario: list-shops removed
- **GIVEN** the blix-scraper CLI
- **WHEN** the command list is retrieved
- **THEN** list-shops is not present

#### Scenario: list-leaflets removed
- **GIVEN** the blix-scraper CLI
- **WHEN** the command list is retrieved
- **THEN** list-leaflets is not present

## Implementation Notes

### File Location

- CLI implementation: `src/cli/__init__.py` (modify existing)

### Commands to Remove

- `list_shops()` function and @app.command() decorator
- `list_leaflets()` function and @app.command() decorator

### Commands to Modify

- `scrape_shops()` - use ScraperService, remove storage
- `scrape_leaflets()` - use ScraperService, remove storage
- `scrape_offers()` - use ScraperService, remove storage
- `search()` - use ScraperService with in-memory date filtering, remove storage

### Commands to Keep

- `scrape_full_shop()` - modify to use ScraperService
- `config()` - keep as-is (no scraping)

### New Dependencies

- `from src.services import ScraperService`

### Backward Compatibility

- All command names remain the same except list-shops and list-leaflets which are removed
- Output format is similar but data is displayed directly from scraping
