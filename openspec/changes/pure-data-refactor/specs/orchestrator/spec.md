# Orchestrator Removal Specifications

**Spec ID**: 04-orchestrator  
**Parent Change**: pure-data-refactor  
**Status**: Draft

## Overview

This specification defines the removal of the ScraperOrchestrator class from the blix-scraper project. The orchestrator is being replaced by the new ScraperService which provides the same functionality without storage integration.

## REMOVED Requirements

### Requirement: ScraperOrchestrator Deletion

The ScraperOrchestrator class SHALL be removed entirely from the codebase.

#### Scenario: Orchestrator file deleted
- **GIVEN** the src/orchestrator.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the file is deleted from the repository
- **AND** the ScraperOrchestrator class no longer exists

#### Scenario: No ScraperOrchestrator imports
- **GIVEN** any module in the codebase
- **WHEN** imports are analyzed
- **THEN** there are no imports of ScraperOrchestrator
- **AND** no code references ScraperOrchestrator

#### Scenario: No orchestrator instantiation
- **GIVEN** any code in the codebase
- **WHEN** the code is executed or analyzed
- **THEN** ScraperOrchestrator is never instantiated

### Requirement: Orchestrator Storage Removal

All storage-related code in orchestrator SHALL be removed.

#### Scenario: shops_storage removed
- **GIVEN** the code that created shops_storage
- **WHEN** the refactor is implemented
- **THEN** no JSONStorage is instantiated for shops

#### Scenario: leaflets_storage removed
- **GIVEN** the code that created leaflets_storage
- **WHEN** the refactor is implemented
- **THEN** no JSONStorage is instantiated for leaflets

#### Scenario: All save operations removed
- **GIVEN** the scrape methods in orchestrator
- **WHEN** the refactor is implemented
- **THEN** there are no calls to storage.save() or storage.save_many()

### Requirement: CLI Orchestrator Imports Removed

All CLI imports of orchestrator SHALL be removed.

#### Scenario: No orchestrator import in CLI
- **GIVEN** the src/cli/__init__.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the import `from ..orchestrator import ScraperOrchestrator` is removed

#### Scenario: No orchestrator usage in CLI
- **GIVEN** the CLI code
- **WHEN** the code is analyzed
- **THEN** ScraperOrchestrator is not used anywhere
- **AND** no `with ScraperOrchestrator() as orchestrator:` blocks exist

### Requirement: Orchestrator Tests Removal

All orchestrator-related tests SHALL be removed.

#### Scenario: Orchestrator test file removed
- **GIVEN** a test file for orchestrator (if it exists)
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the test file is deleted

#### Scenario: No orchestrator in conftest.py
- **GIVEN** the tests/conftest.py file
- **WHEN** the refactor is implemented
- **THEN** no fixtures create ScraperOrchestrator instances
- **AND** no fixtures depend on storage

## Implementation Notes

### Files to Delete

- src/orchestrator.py (entire file)

### Code Changes Required

1. Remove import from src/cli/__init__.py:
   ```python
   # Remove this line:
   from ..orchestrator import ScraperOrchestrator
   ```

2. Replace all orchestrator usage in CLI with ScraperService:
   ```python
   # Old:
   with ScraperOrchestrator(headless=headless) as orchestrator:
       shops = orchestrator.scrape_all_shops()
   
   # New:
   from src.services import ScraperService
   with ScraperService(headless=headless) as service:
       shops = service.get_shops()
   ```

3. Remove all save operations from what becomes ScraperService

### Method Mapping

| Old Orchestrator Method | New Service Method |
|------------------------|-------------------|
| scrape_all_shops() | get_shops() |
| scrape_shop_leaflets(shop_slug) | get_leaflets(shop_slug) |
| scrape_leaflet_offers(shop_slug, leaflet_id) | get_offers(shop, leaflet) |
| scrape_leaflet_keywords(shop_slug, leaflet_id) | get_keywords(shop, leaflet) |
| search_products(query, filter_by_name) | search(query, filter_by_name) |
| scrape_full_leaflet(shop_slug, leaflet_id) | get_offers + get_keywords |
| scrape_all_shop_data(shop_slug, active_only) | Combined workflow |

### Verification

After implementation:
- `ls src/orchestrator.py` should show "No such file or directory"
- `grep -r "ScraperOrchestrator" src/` should return no results
- `grep -r "from ..orchestrator" src/` should return no results
- `grep -r "orchestrator" src/cli/` should return no results
