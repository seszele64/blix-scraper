## ADDED Requirements

### Requirement: System validates field names against entity schema
The system SHALL validate provided field names against available fields for each entity type.

#### Scenario: Valid fields for shop entity
- **WHEN** user specifies `--fields id,name` for shops
- **THEN** the system accepts the fields as valid

#### Scenario: Valid fields for offer entity
- **WHEN** user specifies `--fields id,name,price,shop_name` for offers
- **THEN** the system accepts the fields as valid

#### Scenario: Valid fields for leaflet entity
- **WHEN** user specifies `--fields id,shop_id,title,valid_from` for leaflets
- **THEN** the system accepts the fields as valid

### Requirement: System rejects invalid field names
The system SHALL reject invalid field names with a helpful error message.

#### Scenario: Invalid field for shops
- **WHEN** user specifies `--fields id,invalid_field` for shops
- **THEN** the system displays error: "Invalid field 'invalid_field' for Shop entity. Available fields: id, name, ..."
- **AND** the command exits with non-zero status

#### Scenario: All fields invalid
- **WHEN** user specifies `--fields foo,bar` for any entity
- **THEN** the system displays error listing all invalid fields
- **AND** the command exits with non-zero status

### Requirement: Validation occurs before data fetching
The system SHALL validate fields before making any network requests.

#### Scenario: Early validation prevents unnecessary requests
- **WHEN** user specifies invalid fields
- **THEN** validation fails immediately
- **AND** no HTTP requests are made to blix.pl
