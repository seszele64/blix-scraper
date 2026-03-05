## ADDED Requirements

### Requirement: Field Inclusion Filter
The system SHALL allow users to specify which fields to include in the exported data using the `--fields` CLI option.

#### Scenario: Include specific fields only
- **WHEN** user runs a scrape command with `--fields name,price,shop_name`
- **THEN** the exported JSON SHALL contain only the specified fields for each record
- **AND** other fields SHALL be omitted from the output

#### Scenario: Include single field
- **WHEN** user runs a scrape command with `--fields name`
- **THEN** the exported JSON SHALL contain only the `name` field

#### Scenario: Include all fields (default)
- **WHEN** user runs a scrape command without `--fields` option
- **THEN** the exported JSON SHALL contain all available fields (backward compatible)

#### Scenario: Include fields for nested data (uniform filtering)
- **WHEN** user runs a scrape command with `--fields` for a command that exports nested entities (e.g., `scrape_full_shop`)
- **THEN** the filtering SHALL apply uniformly to all nested objects
- **AND** each nested object (e.g., each offer within a shop) SHALL have the same fields filtered consistently

### Requirement: Field Exclusion Filter
The system SHALL allow users to specify which fields to exclude from the exported data using the `--exclude` CLI option.

#### Scenario: Exclude specific fields
- **WHEN** user runs a scrape command with `--exclude image_url,logo_url`
- **THEN** the exported JSON SHALL contain all fields except `image_url` and `logo_url`

#### Scenario: Combine include and exclude
- **WHEN** user runs a scrape command with both `--fields` and `--exclude`
- **THEN** the exclude option SHALL be applied after include (fields = include_list - exclude_list)
- **AND** the resulting set of fields SHALL be included in the export

#### Scenario: Include and exclude result in no fields
- **WHEN** user runs a scrape command with `--fields` that are all excluded by `--exclude`
- **THEN** the system SHALL warn the user about the empty result
- **AND** the export SHALL proceed with empty objects containing only metadata

#### Scenario: Exclude all fields results in empty
- **WHEN** user runs a scrape command with `--exclude` that removes all fields
- **THEN** the system SHALL warn the user but still export empty objects

### Requirement: Field Validation
The system SHALL validate field names against the entity schema before starting the scrape.

#### Scenario: Invalid field name
- **WHEN** user runs a scrape command with `--fields invalid_field_name`
- **THEN** the system SHALL display an error message listing valid field names
- **AND** the command SHALL exit without scraping

#### Scenario: Invalid exclude field name
- **WHEN** user runs a scrape command with `--exclude invalid_field`
- **THEN** the system SHALL display an error message listing valid field names
- **AND** the command SHALL exit without scraping

#### Scenario: Case-sensitive field names
- **WHEN** user runs a scrape command with `--fields Name` (capital N)
- **THEN** the system SHALL treat this as invalid since field names are case-sensitive
- **AND** the system SHALL suggest the correct case (`name`)

### Requirement: Available Fields List
The system SHALL provide a `--fields-list` option to display available fields for an entity type without running the scraper.

#### Scenario: Show fields list
- **WHEN** user runs any scrape command with `--fields-list`
- **THEN** the system SHALL display a list of available field names for that command's entity type
- **AND** the command SHALL exit without scraping

#### Scenario: Show fields with description
- **WHEN** user runs a scrape command with `--fields-list`
- **THEN** the displayed list SHALL include field names and their types or descriptions

### Requirement: Field Filtering for All Export Commands
The system SHALL support field filtering on all CLI commands that have a `--save` option.

#### Scenario: Field filtering on scrape_shops
- **WHEN** user runs `scrape_shops --fields name,slug --save`
- **THEN** the exported JSON SHALL contain only name and slug for each shop

#### Scenario: Field filtering on search
- **WHEN** user runs `search "kawa" --fields name,price,shop_name --save`
- **THEN** the exported JSON SHALL contain only name, price, and shop_name for each search result

#### Scenario: Field filtering on scrape_leaflets
- **WHEN** user runs `scrape_leaflets biedronka --fields name,valid_from,valid_until --save`
- **THEN** the exported JSON SHALL contain only name, valid_from, and valid_until for each leaflet

#### Scenario: Field filtering on scrape_offers
- **WHEN** user runs `scrape_offers biedronka 123 --fields name,price --save`
- **THEN** the exported JSON SHALL contain only name and price for each offer

#### Scenario: Field filtering on scrape_full_shop
- **WHEN** user runs `scrape_full_shop biedronka --fields name,price --save`
- **THEN** the exported JSON SHALL contain filtered offers with only name and price fields

### Requirement: Metadata Preservation
The system SHALL preserve export metadata (command parameters, execution time, source URLs) regardless of field filtering settings.

#### Scenario: Metadata with filtered fields
- **WHEN** user runs a scrape command with `--fields name --save`
- **THEN** the exported JSON SHALL include a `metadata` section with fields_used, execution_time_ms, source_urls, and other metadata
- **AND** the metadata SHALL reflect the filtered fields in `fields_used`

(End of file - total 113 lines)
