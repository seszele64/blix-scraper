## 1. Utility Functions

- [x] 1.1 Add `get_available_fields(entity_type: str) -> list[str]` function to `src/utils/data_export.py` using Pydantic model introspection (Shop.model_fields.keys()) instead of hardcoded lists
- [x] 1.2 Add `validate_fields(entity_type: str, fields: list[str]) -> list[str]` function to validate field names
- [x] 1.3 Add `filter_fields(data: dict | list[dict], fields: list[str] | None, exclude: list[str] | None) -> dict | list[dict]` function
- [x] 1.4 Add unit tests for new utility functions in `tests/utils/test_data_export.py`
- [x] 1.5 Add fuzzy field name matching with suggestions for invalid fields (e.g., 'Did you mean: name?')

## 2. CLI Options

- [x] 2.1 Create a shared Typer callback for `--fields` option validation
- [x] 2.2 Create a shared Typer callback for `--exclude` option validation
- [x] 2.3 Add `--fields` option to `scrape_shops` command
- [x] 2.4 Add `--fields` option to `search` command
- [x] 2.5 Add `--fields` option to `scrape_leaflets` command
- [x] 2.6 Add `--fields` option to `scrape_offers` command
- [x] 2.7 Add `--fields` option to `scrape_full_shop` command
- [x] 2.8 Add `--exclude` option to all save-enabled commands
- [x] 2.9 Add `--fields-list` option to display available fields

## 3. Export Integration

- [x] 3.1 Update `_export_data()` function to accept `fields` and `exclude` parameters
- [x] 3.2 Wire up field filtering in `_export_data()` to call `filter_fields()`
- [x] 3.3 Update metadata generation to track which fields were included/excluded
- [x] 3.4 Add warning when resulting data would be empty
- [x] 3.5 Add handling for scrape_full_shop nested data filtering - apply filter uniformly to shop, leaflets, and offers

## 4. Testing

- [x] 4.1 Add integration tests for `--fields` option on each command including scrape_full_shop nested data
- [x] 4.2 Add integration tests for `--exclude` option on each command
- [x] 4.3 Add tests for combining `--fields` and `--exclude`
- [x] 4.4 Add tests for invalid field names (error handling)
- [x] 4.5 Add tests for `--fields-list` option

## 5. Documentation

- [x] 5.1 Update CLI help text with field filtering options
- [x] 5.2 Add examples to each command's docstring
- [x] 5.3 Run linter and type checker to ensure code quality

(End of file - total 43 lines)
