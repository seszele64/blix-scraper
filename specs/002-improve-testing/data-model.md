# Data Model: Testing Infrastructure

**Feature**: Improve Testing Infrastructure  
**Created**: 2026-01-16

## Test Fixtures

### TestConfig

| Field | Type | Description |
|-------|------|-------------|
| base_url | str | Base URL for testing |
| timeout | int | Default timeout in seconds |
| headless | bool | Run browser in headless mode |

### MockDriver

| Field | Type | Description |
|-------|------|-------------|
| page_source | str | Mock HTML content |
| current_url | str | Mock current URL |
| title | str | Mock page title |

### TestEntities

| Entity | Attributes | Relationships |
|--------|------------|---------------|
| TestShop | id, name, url | Has many leaflets |
| TestLeaflet | id, shop_id, name | Belongs to shop |
| TestOffer | id, leaflet_id, product | Belongs to leaflet |

## Fixture Scope Strategy

```python
# conftest.py

import pytest
from unittest.mock import MagicMock

@pytest.fixture(scope="session")
def test_config():
    """Session-wide test configuration."""
    return {
        "base_url": "https://test.blix.pl",
        "timeout": 30,
        "headless": True,
    }

@pytest.fixture(scope="function")
def mock_driver():
    """Mock Selenium WebDriver for scraping tests."""
    driver = MagicMock()
    driver.page_source = "<html><body>Test</body></html>"
    driver.current_url = "https://test.blix.pl/shop"
    driver.title = "Test Shop"
    return driver

@pytest.fixture(scope="function")
def sample_html_dir(tmp_path, scope="session"):
    """Directory with sample HTML fixtures."""
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()
    return fixtures_dir
```

## Test Data Patterns

### Parametrized Test Data

```python
@pytest.mark.parametrize("input,expected", [
    ("valid_url", True),
    ("invalid_url", False),
    ("empty_string", False),
])
def test_url_validation(input, expected):
    assert validate_url(input) == expected
```

### Mock Response Patterns

```python
@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "status": "success",
        "data": [
            {"id": 1, "name": "Shop A"},
            {"id": 2, "name": "Shop B"},
        ],
    }
```

## Coverage Tracking

| Metric | Threshold | Measurement Method |
|--------|-----------|-------------------|
| Line Coverage | 70% | pytest-cov |
| Function Coverage | 80% | pytest-cov |
| Branch Coverage | 60% | pytest-cov |
