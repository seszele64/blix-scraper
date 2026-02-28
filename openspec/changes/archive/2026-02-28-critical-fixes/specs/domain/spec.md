# Technical Debt Specification

**Spec ID**: 01-technical-debt  
**Parent Change**: critical-fixes  
**Status**: Draft

## Overview

This specification defines the requirements for addressing critical technical debt in the blix-scraper project. The changes include fixing deprecated datetime usage, implementing retry logic with tenacity, creating hierarchical configuration, and adding utility functions to reduce code duplication.

## ADDED Requirements

### Requirement: Datetime Usage Must Use timezone-aware Datetimes

The system MUST use `datetime.now(timezone.utc)` instead of the deprecated `datetime.utcnow()` for all datetime creation to ensure Python 3.12+ compatibility.

#### Scenario: Creating current timestamp in scraper
- **GIVEN** a `ShopScraper` instance
- **WHEN** extracting a shop entity and creating its `scraped_at` timestamp
- **THEN** the timestamp MUST use `datetime.now(timezone.utc)`

#### Scenario: Creating current timestamp in leaflet scraper
- **GIVEN** a `LeafletScraper` instance
- **WHEN** determining leaflet status by comparing current time
- **THEN** the current time MUST be obtained using `datetime.now(timezone.utc)`

#### Scenario: Creating current timestamp in offer scraper
- **GIVEN** an `OfferScraper` instance
- **WHEN** creating an `Offer` entity with `scraped_at`
- **THEN** the timestamp MUST use `datetime.now(timezone.utc)`

#### Scenario: Creating current timestamp in keyword scraper
- **GIVEN** a `KeywordScraper` instance
- **WHEN** creating a `Keyword` entity
- **THEN** the timestamp MUST use `datetime.now(timezone.utc)`

---

### Requirement: Retry Logic Must Use Tenacity Library

The system MUST use the tenacity library for implementing retry logic instead of custom implementations, as required by the Constitution.

#### Scenario: Retry decorator applied to base scraper
- **GIVEN** `BaseScraper.scrape()` method
- **WHEN** a network request fails
- **THEN** the method MUST be automatically retried using tenacity's `@retry` decorator

#### Scenario: Exponential backoff with jitter
- **GIVEN** a failed HTTP request in `BaseScraper.scrape()`
- **WHEN** tenacity retries the request
- **THEN** the wait time between retries MUST increase exponentially with a random jitter component

#### Scenario: Retry configuration from settings
- **GIVEN** retry settings in the application config
- **WHEN** `BaseScraper.scrape()` performs a retry
- **THEN** the retry parameters (max_attempts, backoff_factor) MUST be read from the config

#### Scenario: Maximum retry attempts respected
- **GIVEN** a URL that consistently returns errors
- **WHEN** the scraper attempts to scrape the URL
- **THEN** the scraper MUST stop after max_attempts and raise an exception

---

### Requirement: Hierarchical Configuration Structure

The system MUST support hierarchical configuration with nested settings, enabling better organization of related configuration options.

#### Scenario: Nested retry settings under scraping
- **GIVEN** the settings model with nested `scraping.retry` structure
- **WHEN** accessing retry configuration
- **THEN** the settings MUST be accessible via `settings.scraping.retry.max_attempts`

#### Scenario: Environment variable override with double-underscore delimiter
- **GIVEN** environment variable `SCRAPING__RETRY__MAX_ATTEMPTS=5`
- **WHEN** the application loads configuration
- **THEN** the retry max_attempts MUST be set to 5

#### Scenario: Backwards compatibility with flat config
- **GIVEN** existing code using flat config keys like `max_retries`
- **WHEN** the application runs
- **THEN** the flat key MUST still work via backwards compatibility property

---

### Requirement: URL Utilities Must Be Centralized

The system MUST provide centralized utility functions for URL handling to reduce code duplication across scrapers.

#### Scenario: Absolutize relative URL
- **GIVEN** a relative URL like `/sklep/biedronka/`
- **WHEN** calling `absolutize_url(relative_url, base_url)`
- **THEN** the function MUST return `https://blix.pl/sklep/biedronka/`

#### Scenario: Absolutize already absolute URL
- **GIVEN** an absolute URL like `https://example.com/page`
- **WHEN** calling `absolutize_url(absolute_url, base_url)`
- **THEN** the function MUST return the URL unchanged

#### Scenario: Absolutize URL with None base
- **GIVEN** a relative URL and None as base_url
- **WHEN** calling `absolutize_url(relative_url, None)`
- **THEN** the function MUST use the default blix.pl base URL

---

### Requirement: BeautifulSoup Handling Must Be Type-Safe

The system MUST provide type-safe helpers for BeautifulSoup operations to reduce type errors in scrapers.

#### Scenario: Safe attribute extraction
- **GIVEN** a BeautifulSoup Tag with an attribute that might be a list
- **WHEN** using a type-safe helper to extract the attribute
- **THEN** the helper MUST return a single value or None, not a list

---

## MODIFIED Requirements

### Requirement: Datetime Import Statement Must Include timezone

The datetime import statement in scraper files MUST be modified to import timezone explicitly.

#### Scenario: Import statement in shop_scraper.py
- **GIVEN** the shop_scraper.py file
- **WHEN** reviewing the import statement
- **THEN** it MUST include `from datetime import datetime, timezone`

#### Scenario: Import statement in leaflet_scraper.py
- **GIVEN** the leaflet_scraper.py file
- **WHEN** reviewing the import statement
- **THEN** it MUST include `from datetime import datetime, timezone`

#### Scenario: Import statement in offer_scraper.py
- **GIVEN** the offer_scraper.py file
- **WHEN** reviewing the import statement
- **THEN** it MUST include `from datetime import datetime, timezone`

#### Scenario: Import statement in keyword_scraper.py
- **GIVEN** the keyword_scraper.py file
- **WHEN** reviewing the import statement
- **THEN** it MUST include `from datetime import datetime, timezone`

---

## Data Flow

### Retry Logic Flow

```
Scraper.scrape(url)
       │
       ▼
┌──────────────────┐
│  Tenacity Retry  │
│    Decorator     │
└────────┬─────────┘
         │
    ┌────▼─────┐
    │ Request  │
    │ Attempt  │
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Success? │
    └────┬─────┘
    Yes  │  No
    ┌────▼──────┐
    │ Return    │   ┌─────────────┐
    │ Entities  │◄──│ Wait with   │
    └───────────┘   │ Exponential │
                    │ Backoff     │
                    └─────────────┘
```

### Configuration Flow

```
Environment Variables
        │
        ▼
┌──────────────────┐
│  Pydantic        │
│  BaseSettings    │
│  (nested)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Settings        │
│  Object          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  BaseScraper     │
│  (uses retry)    │
└──────────────────┘
```

## Type Definitions

### RetrySettings

```python
class RetrySettings(BaseSettings):
    """Retry configuration settings."""
    
    max_attempts: int = Field(default=3, description="Maximum number of retry attempts")
    backoff_factor: float = Field(default=2.0, description="Exponential backoff multiplier")
    jitter: bool = Field(default=True, description="Add random jitter to backoff")
    retry_on_exceptions: tuple = Field(
        default=(TimeoutError, ConnectionError),
        description="Exception types to retry on"
    )
```

### ScrapingSettings

```python
class ScrapingSettings(BaseSettings):
    """Hierarchical scraping configuration."""
    
    request_delay_min: float = Field(default=2.0, description="Minimum delay between requests")
    request_delay_max: float = Field(default=5.0, description="Maximum delay between requests")
    page_load_timeout: int = Field(default=30, description="Page load timeout in seconds")
    
    class retry(RetrySettings):
        """Nested retry configuration."""
        pass
```

### Settings (Main)

```python
class Settings(BaseSettings):
    """Main application settings with backwards compatibility."""
    
    # Backwards compatibility properties
    @property
    def max_retries(self) -> int:
        """Backwards compatible max_retries access."""
        return self.scraping.retry.max_attempts
    
    @property
    def retry_backoff(self) -> float:
        """Backwards compatible retry_backoff access."""
        return self.scraping.retry.backoff_factor
```

## File Locations

- Retry settings: `src/config.py`
- Base scraper with retry: `src/scrapers/base.py`
- URL utilities: `src/utils/url_helpers.py`
- Type-safe soup helpers: `src/utils/soup_helpers.py`
- Affected scrapers: `src/scrapers/shop_scraper.py`, `src/scrapers/leaflet_scraper.py`, `src/scrapers/offer_scraper.py`, `src/scrapers/keyword_scraper.py`

## Dependencies

- `tenacity` - Retry logic library (NEW)
- `pydantic-settings` - Configuration management (existing)
- `structlog` - Structured logging (existing)

## Testing Requirements

### Retry Tests

```python
# tests/scrapers/test_retry.py

class TestRetryLogic:
    
    def test_exponential_backoff_increases(self):
        """Verify backoff increases exponentially."""
        # Test implementation
        
    def test_jitter_adds_randomness(self):
        """Verify jitter adds randomness to wait times."""
        # Test implementation
        
    def test_max_attempts_respected(self):
        """Verify max attempts limit is enforced."""
        # Test implementation
```

### Config Tests

```python
# tests/test_config.py

class TestHierarchicalConfig:
    
    def test_nested_retry_accessible(self):
        """Verify nested retry settings accessible."""
        assert settings.scraping.retry.max_attempts == 3
        
    def test_env_var_override(self, monkeypatch):
        """Verify environment variable override works."""
        monkeypatch.setenv("SCRAPING__RETRY__MAX_ATTEMPTS", "5")
        # Reload settings
        assert settings.scraping.retry.max_attempts == 5
        
    def test_backwards_compatibility(self):
        """Verify flat config keys still work."""
        assert settings.max_retries == settings.scraping.retry.max_attempts
```

### Utility Tests

```python
# tests/utils/test_url_helpers.py

class TestUrlHelpers:
    
    def test_absolutize_relative_url(self):
        """Test converting relative URL to absolute."""
        result = absolutize_url("/sklep/biedronka/", "https://blix.pl")
        assert result == "https://blix.pl/sklep/biedronka/"
        
    def test_absolutize_already_absolute(self):
        """Test absolute URL unchanged."""
        result = absolutize_url("https://example.com/", "https://blix.pl")
        assert result == "https://example.com/"
        
    def test_absolutize_with_default_base(self):
        """Test using default base URL."""
        result = absolutize_url("/sklep/biedronka/", None)
        assert result == "https://blix.pl/sklep/biedronka/"
```
