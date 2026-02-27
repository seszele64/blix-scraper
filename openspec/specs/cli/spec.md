# CLI Commands Date Filtering Specification

**Spec ID**: 03-cli-commands  
**Parent Change**: date-filtering  
**Status**: Draft

## Overview

This specification defines the CLI commands and options for date filtering. The CLI is built using Typer and provides the user-facing interface for filtering leaflets and offers by date.

## ADDED Requirements

### Requirement: Extended `list-leaflets` Command

The `list-leaflets` command MUST accept date filtering options.

#### Scenario: Filter by active_on date
- **WHEN** the command executes (user runs `blix-scraper list-leaflets biedronka --active-on "2024-01-20"`)
- **THEN** only leaflets valid on 2024-01-20 are displayed

#### Scenario: Filter by valid_from
- **WHEN** the command executes (user runs `blix-scraper list-leaflets biedronka --valid-from "next Monday"`)
- **THEN** only leaflets starting from next Monday are displayed

#### Scenario: Filter by valid_until
- **WHEN** the command executes (user runs `blix-scraper list-leaflets biedronka --valid-until "end of month"`)
- **THEN** only leaflets ending by end of month are displayed

#### Scenario: Filter by date range
- **WHEN** the command executes (user runs `blix-scraper list-leaflets carrefour --within-range "2024-02-01 to 2024-02-14"`)
- **THEN** only leaflets with validity overlapping that range are displayed

#### Scenario: Combine date filter with active_only
- **WHEN** the command executes (user runs `blix-scraper list-leaflets biedronka --active-on "today" --active-only`)
- **THEN** only currently active leaflets valid today are displayed

### Requirement: Extended `search` Command

The `search` command MUST accept date filtering options to filter results by leaflet validity.

#### Scenario: Search with active_on filter
- **WHEN** the command executes (user runs `blix-scraper search kawa --active-on "this weekend"`)
- **THEN** only products in leaflets valid on this weekend are shown

#### Scenario: Search with valid_from filter
- **WHEN** the command executes (user runs `blix-scraper search mleko --valid-from "next Monday"`)
- **THEN** products in leaflets starting from next Monday are shown

#### Scenario: Search with valid_until filter
- **WHEN** the command executes (user runs `blix-scraper search chipsy --valid-until "this Sunday"`)
- **THEN** products in leaflets ending by this Sunday are shown

#### Scenario: Search with within_range filter
- **WHEN** the command executes (user runs `blix-scraper search banany --within-range "2024-02-01 to 2024-02-14"`)
- **THEN** products in leaflets overlapping that date range are shown

### Requirement: Date Parsing Service Integration

CLI MUST use a date parsing service to convert user input to datetime.

#### Scenario: Parse ISO date format
- **WHEN** DateParser processes the input (user provides "--active-on 2024-01-20")
- **THEN** it returns datetime(2024, 1, 20) in UTC

#### Scenario: Parse natural language date
- **WHEN** DateParser processes the input (user provides "--active-on 'next Friday'")
- **THEN** it returns the datetime of next Friday

#### Scenario: Invalid date shows error
- **WHEN** DateParser processes the input (user provides "--active-on 'not-a-valid-date'")
- **THEN** a DateParseError is raised with helpful message

### Requirement: Combined Filter Options

CLI MUST support combining multiple date filter options.

#### Scenario: Multiple filters combined with AND
- **WHEN** the command executes (user runs `blix-scraper list-leaflets biedronka --active-on "2024-01-20" --valid-from "2024-01-01"`)
- **THEN** only leaflets valid on that date AND starting from Jan 1st are shown

#### Scenario: Range option takes precedence
- **WHEN** the command executes (user provides both --within-range and individual date options)
- **THEN** --within-range is used and a warning is shown

### Requirement: Help and Error Messages

CLI MUST provide helpful error messages for invalid date inputs.

#### Scenario: Invalid date format shows guidance
- **WHEN** the command fails (user runs `blix-scraper list-leaflets biedronka --active-on "invalid"`)
- **THEN** error message suggests valid formats like "2024-01-20" or natural language

#### Scenario: Empty results shows informative message
- **WHEN** no leaflets match (user runs `blix-scraper list-leaflets biedronka --active-on "2025-01-01"`)
- **THEN** message says "No leaflets found valid on 2025-01-01 for shop biedronka"

#### Scenario: Successful query shows filter info in output
- **WHEN** results are displayed (user runs `blix-scraper list-leaflets biedronka --active-on "this weekend"`)
- **THEN** output shows "Showing X leaflets (filtered by: active-on=2024-01-20)"

#### Scenario: Help text includes all date options
- **WHEN** help text is displayed (user runs `blix-scraper list-leaflets --help`)
- **THEN** all date filtering options are documented with examples

## Option Definitions

### --active-on

| Attribute | Value |
|-----------|-------|
| Type | string (optional) |
| Short | -a |
| Help | Show leaflets valid on this date |
| Example | `--active-on "2024-01-20"` |

### --valid-from

| Attribute | Value |
|-----------|-------|
| Type | string (optional) |
| Short | -f |
| Help | Show leaflets valid from this date onwards |
| Example | `--valid-from "next Monday"` |

### --valid-until

| Attribute | Value |
|-----------|-------|
| Type | string (optional) |
| Short | -u |
| Help | Show leaflets valid until this date |
| Example | `--valid-until "end of month"` |

### --within-range

| Attribute | Value |
|-----------|-------|
| Type | string (optional) |
| Short | -r |
| Help | Show leaflets valid within date range |
| Example | `--within-range "2024-02-01 to 2024-02-14"` |

## Output Formatting

### List Leaflets Output

```
╭─────────────────────────────────────────────────────────────╮
│ Leaflets for biedronka                                       │
├──────┬────────────────────────────────┬────────┬──────────────┤
│ ID   │ Name                          │ Status │ Valid Period │
├──────┼────────────────────────────────┼────────┼──────────────┤
│ 1234 │ Promocje weekendowe           │ active │ 2024-01-19   │
│      │                                │        │ to 2024-01-21│
│ 1235 │ Tanie Zakupy                  │ active │ 2024-01-20   │
│      │                                │        │ to 2024-01-22│
╰──────┴────────────────────────────────┴────────┴──────────────╯
Showing 2 of 15 leaflets (filtered by: active-on=2024-01-20)
```

### Search Output

```
╭─────────────────────────────────────────────────────────────╮
│ Search Results for 'kawa' (valid on 2024-01-20)           │
├──────┬────────────────────┬──────────┬──────────────────────┤
│ Prod │ Brand             │ Price    │ Leaflet (Valid)     │
├──────┼────────────────────┼──────────┼──────────────────────┤
│ Kaw… │ Jacobs            │ 12.99 zł │ 1234 (2024-01-19 to │
│      │                   │          │ 2024-01-21)          │
│ Kaw… │ Tchibo            │ 14.99 zł │ 1235 (2024-01-20 to  │
│      │                   │          │ 2024-01-22)          │
╰──────┴────────────────────┴──────────┴──────────────────────╯
Showing 2 of 45 results (filtered by: active-on=2024-01-20)
```

## Implementation Notes

### File Location

- CLI commands: `src/cli/__init__.py` (modify existing)
- Date parser utility: `src/utils/date_parser.py` (new file)

### Dependencies

- `dateparser>=1.1.0` - Natural language date parsing (add to pyproject.toml)

### Backward Compatibility

- All existing options must continue to work
- Adding new options should not break existing behavior
- Use Typer's default None values to maintain backward compatibility
