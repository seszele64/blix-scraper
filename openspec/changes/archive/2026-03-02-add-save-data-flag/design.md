## Context

The blix-scraper currently fetches promotional leaflet data from blix.pl but only displays results in the terminal using Rich tables. Users have no way to persist this data for later analysis, archival, or integration with other tools.

This change adds CLI options to save scraped data as JSON files, following the project's established pattern of JSON file storage.

## Goals / Non-Goals

**Goals:**
- Add `--save` / `-s` flag to all scrape commands to enable saving output as JSON
- Add `--output` / `-o` option to specify custom output file path
- Maintain backward compatibility - displaying data remains the default behavior
- Follow project's JSON file storage convention from the constitution

**Non-Goals:**
- Database storage - keeping with JSON-only file storage
- CSV or other export formats (JSON only)
- Real-time streaming of data
- Server/API mode - CLI-only for now

## Decisions

1. **CLI Option Design**
   - Use `--save` / `-s` as the flag to enable saving (positive action)
   - Use `--output` / `-o` to specify custom file path
   - Default to stdout (current behavior) unless `--save` is provided

2. **File Naming Convention**
   - Default pattern: `{command}_{entity}_{timestamp}.json`
   - Examples: `search_results_2024-01-15.json`, `scrape_shops_2024-01-15.json`
   - Stored in the project's data directory

3. **JSON Serialization**
   - Use Pydantic's `.model_dump()` with `mode='json'` for proper serialization
   - Include metadata (timestamp, command used, filters applied)
   - Pretty-print JSON for readability

4. **Location for Export Logic**
   - Create new utility module: `src/utils/data_export.py`
   - Reuse existing entity models (Shop, Leaflet, Offer, SearchResult)
   - No changes to existing service layer structure

5. **Alternative Approaches Considered**
   - Environment variable approach: Rejected - CLI flags are more explicit
   - Config file: Overkill for simple save functionality
   - Different flag names (`--json`, `--export`): `--save` is more intuitive

## Risks / Trade-offs

- **Risk**: Users might accidentally overwrite files
  - **Mitigation**: Add confirmation prompt or use unique timestamps by default

- **Risk**: Large datasets could create large files
  - **Mitigation**: Document file size implications; no limit by default

- **Risk**: Breaking change for scripts relying on stdout-only output
  - **Mitigation**: Default remains display-only; must opt-in to save

- **Trade-off**: Adding options to 5 commands = some code duplication
  - **Acceptable**: Each command has different data types; simpler than complex abstraction

## Migration Plan

1. Deploy new CLI options (backward compatible)
2. Document new flags in CLI help and README
3. No migration needed - purely additive feature

## Open Questions

- Should we support appending to existing files? (No, keep simple for v1)
- Should we validate output path exists? (Yes, create parent directories)
