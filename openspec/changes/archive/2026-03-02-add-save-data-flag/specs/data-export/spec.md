## ADDED Requirements

### Requirement: Save data to JSON file
The system SHALL allow users to save scraped data to a JSON file when the `--save` flag is provided to any scrape command.

#### Scenario: Save shops data with flag
- **WHEN** user runs `blix-scraper scrape-shops --save`
- **THEN** system saves shops data to a JSON file in the default data directory (~/.local/share/blix-scraper/ on Linux)
- **AND** displays success message with file path

#### Scenario: Save search results with flag
- **WHEN** user runs `blix-scraper search kawa --save`
- **THEN** system saves search results to a JSON file
- **AND** displays the results in the terminal (current behavior preserved)

#### Scenario: Save leaflets with flag
- **WHEN** user runs `blix-scraper scrape-leaflets biedronka --save`
- **THEN** system saves leaflets data to a JSON file

#### Scenario: Save offers with flag
- **WHEN** user runs `blix-scraper scrape-offers biedronka 123 --save`
- **THEN** system saves offers data to a JSON file

#### Scenario: Save full shop data with flag
- **WHEN** user runs `blix-scraper scrape-full-shop biedronka --save`
- **THEN** system saves complete shop data as a structured object containing:
  - `shop`: Shop entity
  - `leaflets`: List of Leaflet entities
  - `offers`: List of Offer entities
  - `keywords`: List of strings
- **AND** saves to a JSON file

### Requirement: Custom output file path
The system SHALL allow users to specify a custom output file path using the `--output` or `-o` option.

#### Scenario: Specify custom output path
- **WHEN** user runs `blix-scraper search kawa --save --output /path/to/custom.json`
- **THEN** system saves data to the specified path `/path/to/custom.json`

#### Scenario: Output path creates directories
- **WHEN** user runs `blix-scraper search kawa --save --output subdir/nested/file.json`
- **AND** the parent directories do not exist
- **THEN** system creates the directory structure
- **AND** saves the file successfully

### Requirement: Path validation
The system SHALL validate output paths to prevent path traversal attacks and ensure files are written to valid locations.

#### Scenario: Reject path traversal sequences
- **WHEN** user runs `blix-scraper search kawa --save --output data/../../../etc/passwd`
- **THEN** system rejects the path with error message "Invalid output path: path traversal not allowed"
- **AND** exits with code 1

#### Scenario: Sanitize invalid filename characters
- **WHEN** user provides output path with invalid characters (`file:name?.json`)
- **THEN** system sanitizes or rejects the filename
- **AND** saves to valid path

#### Scenario: Allow user home directory paths
- **WHEN** user runs `blix-scraper search kawa --save --output ~/Downloads/results.json`
- **THEN** system resolves the tilde to the user's home directory
- **AND** saves to the resolved absolute path (e.g., `/home/user/Downloads/results.json`)

#### Scenario: Save to relative path in current directory
- **WHEN** user runs `blix-scraper search kawa --save --output ./results.json`
- **THEN** system resolves the relative path from current working directory
- **AND** saves to the resolved absolute path

### Requirement: Error handling for file operations
The system SHALL handle file operation errors gracefully with user-friendly messages and appropriate exit codes.

#### Scenario: Handle permission denied error
- **WHEN** user runs `blix-scraper search kawa --save --output /root/protected.json`
- **AND** the system lacks write permission
- **THEN** system displays error "Cannot write to /root/protected.json: permission denied"
- **AND** exits with code 1

#### Scenario: Handle disk full error
- **WHEN** user runs a scrape command with `--save`
- **AND** the disk is full
- **THEN** system displays error "Failed to save data: disk full"
- **AND** exits with code 1

#### Scenario: Handle serialization failure
- **WHEN** scraped data cannot be serialized to JSON
- **THEN** system displays error "Failed to serialize data: {specific error}"
- **AND** exits with code 1

#### Scenario: Handle directory creation failure
- **WHEN** user specifies output path with nested directories that cannot be created
- **THEN** system displays error "Failed to create directory: {path}"
- **AND** exits with code 1

### Requirement: Default file naming
When `--save` is provided but `--output` is not, the system SHALL use a default file naming pattern.

#### Scenario: Default file name pattern
- **WHEN** user runs `blix-scraper search kawa --save` without `--output`
- **THEN** system saves to `{xdg_data_home}/blix-scraper/search_results_{timestamp}.json`
- **AND** uses ISO 8601 compact timestamp format (e.g., `search_results_20240115T143000.json`)

#### Scenario: Different commands have distinct default names
- **WHEN** user saves data from different commands
- **THEN** each command uses appropriate file prefix with ISO 8601 timestamp:
  - `scrape-shops` → `shops_20240115T143000.json`
  - `search` → `search_results_20240115T143000.json`
  - `scrape-leaflets` → `leaflets_20240115T143000.json`
  - `scrape-offers` → `offers_20240115T143000.json`
  - `scrape-full-shop` → `full_shop_20240115T143000.json`

### Requirement: Date-based directory organization
The system SHALL support optional date-based directory hierarchy for better file organization.

#### Scenario: Enable dated directory structure
- **WHEN** user runs `blix-scraper search kawa --save --dated-dirs`
- **THEN** system saves to `{xdg_data_home}/blix-scraper/2024/01/15/search_results_20240115T143000.json`
- **AND** creates year/month/day subdirectories

#### Scenario: Default flat structure without flag
- **WHEN** user runs `blix-scraper search kawa --save` without `--dated-dirs`
- **THEN** system saves to flat structure `{xdg_data_home}/blix-scraper/search_results_20240115T143000.json`

### Requirement: Backward compatibility
The system SHALL NOT change existing behavior when `--save` is not provided.

#### Scenario: Default behavior unchanged
- **WHEN** user runs `blix-scraper search kawa` without `--save`
- **THEN** system displays results in terminal only
- **AND** no file is created

#### Scenario: All existing options work as before
- **WHEN** user runs any existing command with existing options
- **THEN** behavior remains unchanged
- **AND** only new `--save` and `--output` options are added

### Requirement: JSON output format
Saved JSON files SHALL contain structured data with comprehensive metadata following data engineering best practices.

#### Scenario: JSON includes comprehensive metadata
- **WHEN** data is saved to JSON
- **THEN** the JSON SHALL include a `metadata` object containing:
  - `schema_version`: Semantic version string (e.g., "1.0.0") for data contract versioning
  - `entity_type`: String identifying the data type (e.g., "shops", "search_results", "leaflets", "offers", "full_shop")
  - `export_timestamp`: ISO 8601 format timestamp of when data was saved
  - `tool_version`: Version of blix-scraper that generated the export
  - `tool_name`: "blix-scraper"
  - `record_count`: Integer count of records in the data array
  - `fields`: Array of field specifications with name, type, and description
  - `lineage`: Object containing:
    - `command`: Full CLI command used
    - `parameters`: Object with query parameters and filters applied
    - `source_urls`: Array of source URLs scraped
    - `execution_time_ms`: Integer milliseconds for scrape execution
- **AND** the JSON SHALL include a `data` array containing the actual scraped records

#### Scenario: JSON is pretty-printed
- **WHEN** data is saved to JSON
- **THEN** the file is formatted with indentation for readability

### Requirement: Default data directory location
The system SHALL use XDG Base Directory specification for the default data directory location.

#### Scenario: Linux default location
- **WHEN** user runs a save command on Linux without specifying --output
- **THEN** system saves to `~/.local/share/blix-scraper/`

#### Scenario: macOS default location
- **WHEN** user runs a save command on macOS without specifying --output
- **THEN** system saves to `~/Library/Application Support/blix-scraper/`

#### Scenario: Windows default location
- **WHEN** user runs a save command on Windows without specifying --output
- **THEN** system saves to `%APPDATA%/blix-scraper/`

### Requirement: Custom output location
The system SHALL allow users to save to any valid path when using the --output flag.

#### Scenario: Save to Downloads folder
- **WHEN** user runs `blix-scraper search kawa --save --output ~/Downloads/results.json`
- **THEN** system saves to ~/Downloads/results.json
- **AND** displays success message with full path

#### Scenario: Save to current working directory
- **WHEN** user runs `blix-scraper search kawa --save --output ./data/results.json`
- **THEN** system saves to ./data/results.json relative to current working directory

### Requirement: Schema versioning
The system SHALL maintain a schema version constant for exported data.

#### Scenario: Export includes schema version
- **WHEN** any data is saved to JSON
- **THEN** the `metadata.schema_version` field SHALL be set to "1.0.0"
- **AND** this version SHALL follow semantic versioning (MAJOR.MINOR.PATCH)

#### Scenario: Schema version constant defined
- **WHEN** developers reference the export schema
- **THEN** a `EXPORT_SCHEMA_VERSION` constant SHALL be defined in the codebase
- **AND** it SHALL be used for all exports

### Requirement: Data validation before export
The system SHALL validate data against Pydantic models before writing to file.

#### Scenario: Valid data passes validation
- **WHEN** scraped data matches entity model schema
- **THEN** validation succeeds
- **AND** data is saved with `metadata.validation_status: "passed"`

#### Scenario: Invalid data handled gracefully
- **WHEN** scraped data fails validation
- **THEN** system logs validation errors
- **AND** saves data with `metadata.validation_status: "warning"`
- **AND** includes `metadata.validation_errors` array with details

## Exit Codes

The system SHALL use the following exit codes:
- **0**: Success - data saved successfully (or displayed if no --save flag)
- **1**: Error - various failure conditions including:
  - Path validation failure
  - Permission denied
  - Disk full
  - Serialization failure
  - Directory creation failure
