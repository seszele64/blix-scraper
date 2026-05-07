# Storage Removal Specifications

**Spec ID**: 03-storage  
**Parent Change**: pure-data-refactor  
**Status**: Draft

## Overview

This specification defines the removal of the entire storage module from the blix-scraper project. The storage layer is being eliminated to simplify the architecture and remove tight coupling between scraping and persistence.

## REMOVED Requirements

### Requirement: JSONStorage Removal

JSONStorage SHALL be removed entirely from the codebase.

#### Scenario: JSONStorage class deleted
- **GIVEN** the src/storage/json_storage.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the file is deleted from the repository
- **AND** the JSONStorage class no longer exists

#### Scenario: No JSONStorage imports
- **GIVEN** any module in the codebase
- **WHEN** imports are analyzed
- **THEN** there are no imports of JSONStorage
- **AND** no code references JSONStorage

#### Scenario: No storage instantiation
- **GIVEN** any code in the codebase
- **WHEN** the code is executed or analyzed
- **THEN** JSONStorage is never instantiated

### Requirement: DateFilteredJSONStorage Removal

DateFilteredJSONStorage SHALL be removed entirely from the codebase.

#### Scenario: DateFilteredJSONStorage class deleted
- **GIVEN** the src/storage/date_filtered_storage.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the file is deleted from the repository
- **AND** the DateFilteredJSONStorage class no longer exists

#### Scenario: No DateFilteredJSONStorage imports
- **GIVEN** any module in the codebase
- **WHEN** imports are analyzed
- **THEN** there are no imports of DateFilteredJSONStorage

#### Scenario: No DateFilteredJSONStorage usage
- **GIVEN** any code in the codebase
- **WHEN** the code is executed or analyzed
- **THEN** DateFilteredJSONStorage is never instantiated

### Requirement: FieldFilter Removal

FieldFilter SHALL be removed entirely from the codebase.

#### Scenario: FieldFilter class deleted
- **GIVEN** the src/storage/field_filter.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the file is deleted from the repository
- **AND** the FieldFilter class no longer exists

#### Scenario: No FieldFilter imports
- **GIVEN** any module in the codebase
- **WHEN** imports are analyzed
- **THEN** there are no imports of FieldFilter

#### Scenario: No FieldFilter usage
- **GIVEN** any code in the codebase
- **WHEN** the code is executed or analyzed
- **THEN** FieldFilter is never instantiated

### Requirement: Storage Module Deletion

The entire storage module SHALL be deleted from src/storage/.

#### Scenario: Storage directory deleted
- **GIVEN** the src/storage/ directory
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the entire directory is deleted
- **AND** no files remain in src/storage/

#### Scenario: Storage __init__.py deleted
- **GIVEN** the src/storage/__init__.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the file is deleted

#### Scenario: Storage module not importable
- **GIVEN** Python code attempting to import from src.storage
- **WHEN** the import is executed
- **THEN** a ModuleNotFoundError is raised

### Requirement: Storage Tests Removal

All storage tests SHALL be removed.

#### Scenario: test_json_storage.py deleted
- **GIVEN** the tests/storage/test_json_storage.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the file is deleted from the repository

#### Scenario: test_date_filtered_storage.py deleted
- **GIVEN** the tests/storage/test_date_filtered_storage.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the file is deleted from the repository

#### Scenario: test_field_filter.py deleted
- **GIVEN** the tests/storage/test_field_filter.py file
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the file is deleted from the repository

#### Scenario: Storage tests directory deleted
- **GIVEN** the tests/storage/ directory
- **WHEN** the pure-data-refactor change is implemented
- **THEN** the entire directory is deleted

### Requirement: No FieldFilter in Orchestrator

The orchestrator SHALL NOT use FieldFilter after refactoring.

#### Scenario: FieldFilter removed from orchestrator
- **GIVEN** the orchestrator code (which will be deleted)
- **WHEN** the refactor is implemented
- **THEN** FieldFilter is not imported or used anywhere

## Implementation Notes

### Files to Delete

```
src/storage/__init__.py
src/storage/json_storage.py
src/storage/date_filtered_storage.py
src/storage/field_filter.py
tests/storage/__init__.py
tests/storage/test_json_storage.py
tests/storage/test_date_filtered_storage.py
tests/storage/test_field_filter.py
tests/storage/__pycache__/  (directory)
tests/storage/  (directory)
```

### Code Changes Required

1. Remove all imports of storage classes from:
   - src/orchestrator.py (will be deleted)
   - src/cli/__init__.py

2. Update conftest.py to remove storage-related fixtures if any exist

3. Update test_cli.py to remove tests that depend on storage (list_shops, list_leaflets)

### Verification

After implementation:
- `ls src/storage/` should show "No such file or directory"
- `ls tests/storage/` should show "No such file or directory"
- `grep -r "JSONStorage" src/` should return no results
- `grep -r "FieldFilter" src/` should return no results
- `grep -r "DateFilteredJSONStorage" src/` should return no results
