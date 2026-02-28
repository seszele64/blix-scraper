# Technical Design: Critical Technical Debt Fixes

**Parent Change**: critical-fixes  
**Status**: Draft

## Technical Approach

### Overview

This design addresses four critical technical debt items in the blix-scraper project:

1. **Fix datetime.utcnow() deprecation** - Replace deprecated method with timezone-aware alternative
2. **Implement retry with tenacity** - Add resilience to network failures
3. **Hierarchical configuration** - Organize settings with nested structures
4. **Utility functions** - Centralize common URL and type-safe operations

### Core Principles

1. **Minimal Breaking Changes**: Maintain backwards compatibility for existing config keys
2. **Constitution Compliance**: Use tenacity library as required by project constitution
3. **Python 3.11+ Compatibility**: All datetime operations must use timezone-aware datetimes
4. **Type Safety**: Reduce mypy errors through proper type hints and utilities

---

## Architecture Decisions

### Decision 1: Use datetime.now(timezone.utc) Instead of datetime.utcnow()

**Description**: Replace all instances of deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`.

**Files Affected**:
- `src/scrapers/shop_scraper.py` - Line 130
- `src/scrapers/leaflet_scraper.py` - Lines 124, 152
- `src/scrapers/offer_scraper.py` - Line 161
- `src/scrapers/keyword_scraper.py` - Line 105
- `src/domain/entities.py` - Already fixed (uses default_factory)

| Pros | Cons |
|------|------|
| Python 3.12+ compatible | Requires updating import statements |
| Timezone-aware by default | None |
| Follows modern Python best practices | - |
| Fixes mypy type errors | - |

**Decision**: APPROVED - Eliminates deprecation warnings and improves type safety.

---

### Decision 2: Apply Tenacity Retry Decorator to BaseScraper.scrape()

**Description**: Use tenacity library to wrap the `scrape()` method with retry logic.

**Implementation**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

class BaseScraper(ABC, Generic[T]):
    
    @retry(
        stop=stop_after_attempt(settings.scraping.retry.max_attempts),
        wait=wait_exponential_jitter(
            multiplier=settings.scraping.retry.backoff_factor,
            max=60
        ),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True
    )
    def scrape(self, url: str) -> List[T]:
        # existing implementation
```

| Pros | Cons |
|------|------|
| Constitution-compliant (uses tenacity) | Adds dependency |
| Configurable retry parameters | Increases method complexity |
| Exponential backoff with jitter | None |
| Battle-tested library | - |

**Decision**: APPROVED - Meets Constitution requirement for retry logic with exponential backoff.

---

### Decision 3: Nested Configuration Under scraping.retry

**Description**: Organize retry settings hierarchically under `scraping.retry` namespace.

**Structure**:
```python
class ScrapingSettings(BaseSettings):
    request_delay_min: float = 2.0
    request_delay_max: float = 5.0
    page_load_timeout: int = 30
    
    class retry(RetrySettings):
        """Nested retry configuration."""
        pass

class RetrySettings(BaseSettings):
    max_attempts: int = 3
    backoff_factor: float = 2.0
    jitter: bool = True
```

| Pros | Cons |
|------|------|
| Organized configuration | Requires property for backwards compat |
| Environment variable support | Slightly more complex model |
| Self-documenting structure | - |
| Scalable for future settings | - |

**Decision**: APPROVED - Improves configuration organization while maintaining backwards compatibility.

---

### Decision 4: Create URL Utilities Module

**Description**: Create centralized utility functions for URL handling.

**Implementation**:
```python
# src/utils/url_helpers.py

DEFAULT_BASE_URL = "https://blix.pl"

def absolutize_url(url: str, base_url: str | None = None) -> str:
    """Convert relative URL to absolute URL.
    
    Args:
        url: The URL to absolutize (can be relative or absolute)
        base_url: The base URL to use for relative URLs
        
    Returns:
        Absolute URL string
    """
    base = base_url or DEFAULT_BASE_URL
    
    if not url:
        return base
    
    if url.startswith(("http://", "https://")):
        return url
    
    # Handle relative URLs
    if url.startswith("/"):
        return f"{base.rstrip('/')}{url}"
    
    return f"{base}/{url}"
```

| Pros | Cons |
|------|------|
| Reduces code duplication | New module to maintain |
| Consistent URL handling | Requires updating existing code |
| Testable in isolation | - |
| Default base URL support | - |

**Decision**: APPROVED - Reduces duplication and improves consistency.

---

### Decision 5: Add Type-Safe BeautifulSoup Helpers

**Description**: Create helpers for type-safe attribute extraction from BeautifulSoup elements.

**Implementation**:
```python
# src/utils/soup_helpers.py

from bs4 import BeautifulSoup, Tag

def get_single_attribute(tag: Tag | None, attr: str) -> str | None:
    """Safely get a single attribute value from a tag.
    
    BeautifulSoup sometimes returns lists for attributes.
    This helper ensures a single value is returned.
    
    Args:
        tag: BeautifulSoup Tag or None
        attr: Attribute name
        
    Returns:
        Single attribute value or None
    """
    if tag is None:
        return None
    
    value = tag.get(attr)
    
    if value is None:
        return None
    
    if isinstance(value, list):
        return value[0] if value else None
    
    return value
```

| Pros | Cons |
|------|------|
| Fixes type errors from list attributes | New module to maintain |
| Reusable across scrapers | None |
| Improves mypy compliance | - |

**Decision**: APPROVED - Fixes type errors and reduces boilerplate.

---

## Data Flow

### Retry Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      User (CLI)                                       │
│  blix-scraper scrape-shops                                           │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BaseScraper.scrape()                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  @retry Decorator                                           │   │
│  │  - stop_after_attempt(3)                                    │   │
│  │  - wait_exponential_jitter(multiplier=2.0, max=60)        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌───────────────┐         ┌───────────────┐
            │  Request 1    │         │  Request 2    │
            │  Failed       │         │  (retry)      │
            │  (timeout)    │         │  Succeeded    │
            └───────────────┘         └───────────────┘
                    │                         │
                    │  Wait with             │
                    │  exponential           │
                    │  backoff + jitter      │
                    └────────────────────────┘
```

### Configuration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Environment Variables                             │
│  SCRAPING__RETRY__MAX_ATTEMPTS=5                                   │
│  SCRAPING__RETRY__BACKOFF_FACTOR=3.0                                │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Pydantic BaseSettings                             │
│  - Nested models with __ delimiter support                          │
│  - Backwards compatibility properties                                │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Settings Object                                   │
│  settings.scraping.retry.max_attempts  # 5                         │
│  settings.scraping.retry.backoff_factor  # 3.0                     │
│  settings.max_retries  # 5 (backwards compat property)             │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BaseScraper Uses Config                           │
│  @retry(stop=stop_after_attempt(settings.scraping.retry.max_attempts))
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Changes

### Files to Create

| File | Purpose |
|------|---------|
| `src/utils/url_helpers.py` | URL absolutization utility |
| `src/utils/soup_helpers.py` | Type-safe BeautifulSoup helpers |
| `tests/utils/test_url_helpers.py` | Tests for URL utilities |
| `tests/utils/test_soup_helpers.py` | Tests for soup helpers |

### Files to Modify

| File | Changes |
|------|---------|
| `src/config.py` | Add nested ScrapingSettings and RetrySettings |
| `src/scrapers/base.py` | Add tenacity retry decorator |
| `src/scrapers/shop_scraper.py` | Fix datetime.utcnow() |
| `src/scrapers/leaflet_scraper.py` | Fix datetime.utcnow() |
| `src/scrapers/offer_scraper.py` | Fix datetime.utcnow() |
| `src/scrapers/keyword_scraper.py` | Fix datetime.utcnow() |
| `src/utils/__init__.py` | Export new utility functions |
| `tests/test_config.py` | Add hierarchical config tests |
| `tests/scrapers/test_base.py` | Add retry logic tests |

### Files to Delete

None.

---

## Component Mapping

### New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `absolutize_url()` | `src/utils/url_helpers.py` | URL absolutization |
| `get_single_attribute()` | `src/utils/soup_helpers.py` | Type-safe attribute extraction |
| `RetrySettings` | `src/config.py` | Retry configuration model |
| `ScrapingSettings` | `src/config.py` | Scraping configuration model |

### Modified Components

| Component | Change |
|-----------|--------|
| `BaseScraper.scrape()` | Added tenacity retry decorator |
| `Settings` | Added nested settings, backwards compat properties |
| `ShopScraper` | datetime.utcnow() → datetime.now(timezone.utc) |
| `LeafletScraper` | datetime.utcnow() → datetime.now(timezone.utc) |
| `OfferScraper` | datetime.utcnow() → datetime.now(timezone.utc) |
| `KeywordScraper` | datetime.utcnow() → datetime.now(timezone.utc) |

---

## Breaking Changes

### Configuration Breaking Changes

| ID | Change | Description | Migration |
|----|--------|-------------|-----------|
| B1 | Flat config keys deprecated | `max_retries` → `scraping.retry.max_attempts` | Use property for backwards compat |

### Behavior Changes

| ID | Change | Description | Impact |
|----|--------|-------------|--------|
| BH1 | Automatic retries | Failed requests now retried | May increase scraping duration |
| BH2 | New dependencies | Tenacity added | `uv sync` required |

### Version Bump Recommendation

**Recommended Version**: v0.2.1

Since changes are backwards compatible and additive (new features without breaking existing APIs), a PATCH version bump is appropriate.

---

## Testing Strategy

### Unit Tests for Retry Logic

```python
# tests/scrapers/test_base.py

class TestRetryLogic:
    
    def test_exponential_backoff_increases(self):
        """Verify backoff wait time increases with each retry."""
        # Test implementation
        
    def test_jitter_adds_randomness(self):
        """Verify jitter adds randomness to wait times."""
        # Test implementation
        
    def test_max_attempts_respected(self):
        """Verify max attempts limit is enforced."""
        # Test implementation
        
    def test_retry_on_specific_exceptions(self):
        """Verify retry only on configured exceptions."""
        # Test implementation
```

### Unit Tests for Hierarchical Config

```python
# tests/test_config.py

class TestHierarchicalConfig:
    
    def test_nested_retry_accessible(self):
        """Verify nested retry settings accessible via dot notation."""
        assert settings.scraping.retry.max_attempts == 3
        
    def test_env_var_override_with_double_underscore(self):
        """Verify environment variable override works with __ delimiter."""
        monkeypatch.setenv("SCRAPING__RETRY__MAX_ATTEMPTS", "5")
        # Reload settings
        assert settings.scraping.retry.max_attempts == 5
        
    def test_backwards_compatibility_flat_keys(self):
        """Verify flat config keys still work via properties."""
        assert settings.max_retries == settings.scraping.retry.max_attempts
        
    def test_backwards_compatibility_retry_backoff(self):
        """Verify retry_backoff property works."""
        assert settings.retry_backoff == settings.scraping.retry.backoff_factor
```

### Unit Tests for URL Utilities

```python
# tests/utils/test_url_helpers.py

class TestAbsolutizeUrl:
    
    def test_relative_url_with_base(self):
        """Test converting relative URL to absolute."""
        result = absolutize_url("/sklep/biedronka/", "https://blix.pl")
        assert result == "https://blix.pl/sklep/biedronka/"
        
    def test_already_absolute_url(self):
        """Test absolute URL unchanged."""
        result = absolutize_url("https://example.com/page", "https://blix.pl")
        assert result == "https://example.com/page"
        
    def test_relative_url_default_base(self):
        """Test using default base URL."""
        result = absolutize_url("/sklep/biedronka/", None)
        assert result == "https://blix.pl/sklep/biedronka/"
        
    def test_empty_url_returns_base(self):
        """Test empty URL returns base URL."""
        result = absolutize_url("", "https://blix.pl")
        assert result == "https://blix.pl"
        
    def test_http_url_returns_unchanged(self):
        """Test HTTP URL returns unchanged."""
        result = absolutize_url("http://example.com/", "https://blix.pl")
        assert result == "http://example.com/"
```

### Integration Tests

```python
# tests/scrapers/test_retry_integration.py

class TestRetryIntegration:
    
    def test_scraper_retries_on_timeout(self, mock_driver):
        """Test that scraper retries on timeout exception."""
        # Mock driver that fails first time, succeeds second
        # Verify retry occurs
```

### Test Coverage Goals

| Module | Target Coverage |
|--------|-----------------|
| `src/config.py` | 85% |
| `src/scrapers/base.py` | 80% |
| `src/utils/url_helpers.py` | 90% |
| `src/utils/soup_helpers.py` | 90% |

---

## Error Handling

### Retry Error Handling

```python
from tenacity import RetryCallState

def log_retry(retry_state: RetryCallState) -> None:
    """Log retry attempt."""
    logger.warning(
        "retry_attempt",
        attempt=retry_state.attempt_number,
        exception=retry_state.outcome.exception()
    )
```

### Configuration Error Handling

```python
# Invalid env vars should not crash - use defaults
# Log warnings for unknown configuration keys
```

---

## Logging

### Retry Logging

```python
from tenacity import before_sleep_log

logger = structlog.get_logger(__name__)

@retry(
    # ... config
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def scrape(self, url: str) -> List[T]:
    # implementation
```

---

## Dependencies

### New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| tenacity | >=8.2.0 | Retry logic library |

### Updated pyproject.toml

```toml
[project.optional-dependencies]
dev = [
    # existing deps
]
scraper = [
    "selenium>=4.0.0",
    "webdriver-manager>=4.0.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=4.9.0",
    "tenacity>=8.2.0",  # NEW
]
```

---

## Performance Considerations

1. **Retry Overhead**: Adding retries may slightly increase total scraping time when failures occur
2. **Jitter Benefits**: Random jitter helps prevent thundering herd on shared networks
3. **Config Lookup**: Nested config lookups are fast (Pydantic caches)
4. **Utility Functions**: Minimal overhead - pure functions with no side effects

---

## Backward Compatibility

### Config Backwards Compatibility

```python
class Settings(BaseSettings):
    """Main settings with backwards compatibility."""
    
    scraping: ScrapingSettings = ScrapingSettings()
    
    # Backwards compatibility properties
    @property
    def max_retries(self) -> int:
        """Backwards compatible max_retries access."""
        return self.scraping.retry.max_attempts
    
    @property
    def retry_backoff(self) -> float:
        """Backwards compatible retry_backoff access."""
        return self.scraping.retry.backoff_factor
    
    # Allow flat keys to still work via __init__ override
    def __init__(self, **data):
        # Handle legacy flat keys
        if "max_retries" in data:
            if "scraping" not in data:
                data["scraping"] = {}
            if "retry" not in data["scraping"]:
                data["scraping"]["retry"] = {}
            data["scraping"]["retry"]["max_attempts"] = data.pop("max_retries")
        # ... similar for retry_backoff
        super().__init__(**data)
```

---

## Appendix: File Manifest

### After Implementation

```
src/
├── config.py                    # MODIFIED - Hierarchical config
├── scrapers/
│   ├── __init__.py
│   ├── base.py                 # MODIFIED - Added tenacity retry
│   ├── shop_scraper.py         # MODIFIED - datetime fix
│   ├── leaflet_scraper.py      # MODIFIED - datetime fix
│   ├── offer_scraper.py        # MODIFIED - datetime fix
│   ├── keyword_scraper.py      # MODIFIED - datetime fix
│   └── search_scraper.py       # UNCHANGED
├── utils/
│   ├── __init__.py             # MODIFIED - Export utilities
│   ├── url_helpers.py          # NEW - URL utilities
│   ├── soup_helpers.py         # NEW - Type-safe soup helpers
│   └── date_parser.py          # UNCHANGED
├── domain/
│   ├── entities.py             # UNCHANGED (already fixed)
│   └── ...
└── ...

tests/
├── test_config.py              # MODIFIED - Add config tests
├── scrapers/
│   ├── test_base.py            # MODIFIED - Add retry tests
│   └── ...
└── utils/
    ├── __init__.py
    ├── test_url_helpers.py     # NEW
    └── test_soup_helpers.py    # NEW
```
