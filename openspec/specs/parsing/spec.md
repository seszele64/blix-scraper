# Date Parsing and Validation Specification

**Spec ID**: 04-date-parsing  
**Parent Change**: date-filtering  
**Status**: Draft

## Overview

This specification defines the date parsing and validation requirements for the date filtering feature. The system must parse various date formats from CLI input and convert them to datetime objects for filtering.

## ADDED Requirements

### Requirement: Date Parser Service

The system MUST provide a date parsing service that converts string inputs to datetime objects.

#### Scenario: Parse ISO date successfully
- **WHEN** DateParser.parse() is called (input "2024-01-20")
- **THEN** it returns datetime(2024, 1, 20) with UTC timezone

#### Scenario: Parse ISO date with time
- **WHEN** DateParser.parse() is called (input "2024-01-20T10:30:00")
- **THEN** it returns datetime with time component preserved

#### Scenario: Parse invalid date raises error
- **WHEN** DateParser.parse() is called (input "not-a-date")
- **THEN** DateParseError is raised

### Requirement: Supported Date Formats

The date parser MUST support the following date formats.

#### Scenario: Parse US date format
- **WHEN** DateParser.parse() is called (input "01/20/2024")
- **THEN** it returns datetime(2024, 1, 20)

#### Scenario: Parse EU date format
- **WHEN** DateParser.parse() is called (input "20.01.2024")
- **THEN** it returns datetime(2024, 1, 20)

#### Scenario: Parse EU alternative format
- **WHEN** DateParser.parse() is called (input "20/01/2024")
- **THEN** it returns datetime(2024, 1, 20)

### Requirement: Natural Language Date Handling

The date parser MUST use dateparser library for natural language processing.

#### Scenario: Parse "today"
- **WHEN** DateParser.parse() is called (input "today")
- **THEN** it returns current date

#### Scenario: Parse "tomorrow"
- **WHEN** DateParser.parse() is called (input "tomorrow")
- **THEN** it returns tomorrow's date

#### Scenario: Parse "yesterday"
- **WHEN** DateParser.parse() is called (input "yesterday")
- **THEN** it returns yesterday's date

#### Scenario: Parse relative day "next Friday"
- **WHEN** DateParser.parse() is called (input "next Friday")
- **THEN** it returns the date of next Friday

#### Scenario: Parse "this weekend"
- **WHEN** DateParser.parse() is called (input "this weekend")
- **THEN** it returns weekend date range

#### Scenario: Parse "next week"
- **WHEN** DateParser.parse() is called (input "next week")
- **THEN** it returns date one week from now

#### Scenario: Parse "end of month"
- **WHEN** DateParser.parse() is called (input "end of month")
- **THEN** it returns last day of current month

#### Scenario: Parse relative days "in 3 days"
- **WHEN** DateParser.parse() is called (input "in 3 days")
- **THEN** it returns date 3 days from now

### Requirement: Range Parsing

The date parser MUST support parsing date range strings.

#### Scenario: Parse range with "to" separator
- **WHEN** DateParser.parse_range() is called (input "2024-01-01 to 2024-01-31")
- **THEN** it returns tuple (datetime(2024,1,1), datetime(2024,1,31))

#### Scenario: Parse range with dash separator
- **WHEN** DateParser.parse_range() is called (input "2024-01-01 - 2024-01-31")
- **THEN** it returns tuple of start and end dates

#### Scenario: Parse range with natural language
- **WHEN** DateParser.parse_range() is called (input "next Monday to next Friday")
- **THEN** it returns tuple of Monday and Friday dates

#### Scenario: Invalid range format raises error
- **WHEN** DateParser.parse_range() is called (input "2024-01-01")
- **THEN** DateParseError is raised

#### Scenario: End date before start date raises error
- **WHEN** DateParser.parse_range() is called (input "2024-01-31 to 2024-01-01")
- **THEN** DateParseError is raised

### Requirement: Date Validation

The system MUST validate parsed dates.

#### Scenario: Date too far in past raises error
- **WHEN** DateParser validates the date (input "2019-01-01")
- **THEN** DateParseError is raised with past date message

#### Scenario: Date too far in future raises error
- **WHEN** DateParser validates the date (input "2030-01-01")
- **THEN** DateParseError is raised with future date message

#### Scenario: Valid recent date passes validation
- **WHEN** DateParser validates the date (input "2024-01-01")
- **THEN** no error is raised

#### Scenario: Invalid calendar date raises error
- **WHEN** DateParser parses the date (input "2024-02-30")
- **THEN** DateParseError is raised

### Requirement: Timezone Handling

The system MUST handle timezones consistently.

#### Scenario: Naive datetime treated as UTC
- **WHEN** DateParser.parse() is called (input "2024-01-20" with no timezone)
- **THEN** returned datetime has UTC timezone

#### Scenario: Parse timezone-aware input
- **WHEN** DateParser.parse() is called (input "2024-01-20T10:30:00+02:00")
- **THEN** datetime is converted to UTC

#### Scenario: Format for display uses local timezone
- **WHEN** formatting for display (UTC datetime)
- **THEN** it shows local timezone representation

### Requirement: Error Handling

The system MUST provide clear error messages for unparseable dates.

#### Scenario: Unparseable date shows suggestion
- **WHEN** DateParseError is raised (input "not-a-date")
- **THEN** message suggests valid formats

#### Scenario: Invalid day shows specific error
- **WHEN** DateParseError is raised (input "32/01/2024")
- **THEN** message explains day is invalid

#### Scenario: Invalid month shows specific error
- **WHEN** DateParseError is raised (input "2024-13-01")
- **THEN** message explains month must be 1-12

#### Scenario: Past date shows helpful message
- **WHEN** DateParseError is raised (input "2019-01-01")
- **THEN** message suggests using date from 2020 or later

#### Scenario: Future date shows helpful message
- **WHEN** DateParseError is raised (input "2030-01-01")
- **THEN** message suggests using date within 2 years

## File Location

- Date parser: `src/utils/date_parser.py` (new file)
- Tests: `tests/utils/test_date_parser.py` (new file)

## Dependencies

- `dateparser>=1.1.0` - Natural language date parsing
