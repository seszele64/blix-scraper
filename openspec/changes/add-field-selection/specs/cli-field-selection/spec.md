## ADDED Requirements

### Requirement: CLI accepts fields option
The CLI SHALL accept a `--fields` option for all commands that produce entity output.

#### Scenario: User specifies fields for shops command
- **WHEN** user runs `blix-scraper shops --fields id,name`
- **THEN** the command processes only the `id` and `name` fields

#### Scenario: User specifies fields for leaflets command
- **WHEN** user runs `blix-scraper leaflets --fields id,shop_id,title`
- **THEN** the command processes only the specified fields

#### Scenario: User specifies fields for offers command
- **WHEN** user runs `blix-scraper offers --fields id,name,price`
- **THEN** the command processes only the specified fields

### Requirement: Fields option accepts comma-separated values
The `--fields` option SHALL accept a comma-separated list of field names without spaces.

#### Scenario: Valid comma-separated fields
- **WHEN** user specifies `--fields id,name,price`
- **THEN** the system parses three fields: `id`, `name`, `price`

#### Scenario: Single field selection
- **WHEN** user specifies `--fields name`
- **THEN** the system parses one field: `name`

### Requirement: Default behavior includes all fields
When `--fields` is not specified, the system SHALL include all available fields.

#### Scenario: No fields option provided
- **WHEN** user runs command without `--fields` option
- **THEN** the system includes all entity fields in output
