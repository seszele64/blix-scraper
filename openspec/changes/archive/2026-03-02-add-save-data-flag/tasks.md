## 1. Data Export Utility

- [x] 1.1 Create `src/utils/data_export.py` module
- [x] 1.2 Implement `save_to_json()` function with data and file path parameters
- [x] 1.3 Add `generate_default_filename()` function for timestamped default names
- [x] 1.4 Add `_build_metadata()` function for JSON header information
- [x] 1.5 Add `ensure_directory_exists()` function for creating output directories

## 2. CLI Updates - Base Support

- [x] 2.1 Add `--save` / `-s` option to CLI base (if possible) or individual commands
- [x] 2.2 Add `--output` / `-o` option for custom file path

## 3. CLI Updates - Individual Commands

- [x] 3.1 Add `--save` and `--output` options to `scrape_shops` command
- [x] 3.2 Add `--save` and `--output` options to `search` command
- [x] 3.3 Add `--save` and `--output` options to `scrape_leaflets` command
- [x] 3.4 Add `--save` and `--output` options to `scrape_offers` command
- [x] 3.5 Add `--save` and `--output` options to `scrape_full_shop` command

## 4. Integration Logic

- [x] 4.1 Integrate data export into `scrape_shops` - serialize and save Shop list
- [x] 4.2 Integrate data export into `search` - serialize and save SearchResult list
- [x] 4.3 Integrate data export into `scrape_leaflets` - serialize and save Leaflet list
- [x] 4.4 Integrate data export into `scrape_offers` - serialize and save Offer list
- [x] 4.5 Integrate data export into `scrape_full_shop` - serialize complete data dict
- [x] 4.6 Add success message with file path after save

## 5. Testing

- [x] 5.1 Write unit tests for `data_export.py` module
- [x] 5.2 Test default filename generation
- [x] 5.3 Test metadata building
- [x] 5.4 Test directory creation
- [x] 5.5 Verify JSON serialization of entity models

## 6. Validation

- [x] 6.1 Run `ruff check` to ensure code quality
- [x] 6.2 Run `ruff format` to ensure formatting
- [x] 6.3 Run `mypy src/` for type checking
- [x] 6.4 Run pytest to verify existing tests pass

## 7. Documentation

- [x] 7.1 Verify CLI help text shows new options
- [ ] 7.2 Update README.md with new feature documentation (optional)

(End of file - total 49 lines)
