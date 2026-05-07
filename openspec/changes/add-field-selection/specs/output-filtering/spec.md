## ADDED Requirements

### Requirement: Field filtering applied to JSON output
The system SHALL filter entity fields before serializing to JSON files.

#### Scenario: Filtered JSON output for shops
- **GIVEN** shops have fields: id, name, address, phone
- **WHEN** user specifies `--fields id,name`
- **THEN** the JSON output contains only `id` and `name` fields per shop

#### Scenario: Filtered JSON output for offers
- **GIVEN** offers have fields: id, name, price, description, image_url
- **WHEN** user specifies `--fields name,price`
- **THEN** the JSON output contains only `name` and `price` fields per offer

### Requirement: Field filtering applied to terminal output
The system SHALL filter entity fields displayed in terminal output.

#### Scenario: Filtered terminal display
- **GIVEN** command outputs to terminal
- **WHEN** user specifies `--fields id,name`
- **THEN** only `id` and `name` columns are displayed

#### Scenario: Terminal display with default fields
- **GIVEN** command outputs to terminal
- **WHEN** user does not specify `--fields`
- **THEN** all fields are displayed in columns

### Requirement: Filtering preserves data types
The system SHALL preserve original data types when filtering fields.

#### Scenario: Price field remains decimal
- **GIVEN** offer price is stored as Decimal
- **WHEN** user specifies `--fields price`
- **THEN** the price field maintains Decimal type in output

#### Scenario: Date fields remain datetime
- **GIVEN** valid_from is a datetime object
- **WHEN** user specifies `--fields valid_from`
- **THEN** the valid_from field maintains datetime type in output

### Requirement: Empty field list results in empty objects
When valid fields are specified but entity lacks those fields, the system SHALL output empty objects.

#### Scenario: Entity missing specified fields
- **GIVEN** an offer entity does not have a `discount` field
- **WHEN** user specifies `--fields discount`
- **THEN** the output contains empty objects or null values for that field
