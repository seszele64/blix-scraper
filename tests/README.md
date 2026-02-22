# Testing Guide

This directory contains the test suite for the blix-scraper project. Tests are written using pytest and follow the Arrange-Act-Assert (AAA) pattern.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Running Tests](#running-tests)
3. [Test Organization](#test-organization)
4. [Available Fixtures](#available-fixtures)
5. [Writing Tests](#writing-tests)
6. [Test Markers](#test-markers)
7. [Mocking Guidelines](#mocking-guidelines)
8. [Examples](#examples)
9. [Contribution Guidelines](#contribution-guidelines)

---

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and pytest configuration
├── fixtures/
│   ├── html/                   # Real HTML samples from blix.pl
│   │   ├── shops_page.html
│   │   ├── leaflet_page.html
│   │   └── offer_page.html
│   └── __init__.py
├── domain/
│   └── test_entities.py        # Pydantic entity tests
├── scrapers/
│   ├── test_shop_scraper.py
│   ├── test_leaflet_scraper.py
│   ├── test_offer_scraper.py
│   ├── test_keyword_scraper.py
│   ├── test_search_scraper.py
│   └── test_base.py
├── storage/
│   ├── test_json_storage.py
│   └── test_field_filter.py
├── cli/
│   └── test_cli.py
└── utils/
    └── capture_html.py         # Utility for capturing HTML fixtures
```

### Directory Layout

- **`conftest.py`**: Shared fixtures available to all tests
- **`fixtures/`**: Test data and HTML samples
- **`domain/`**: Tests for Pydantic entities (Shop, Leaflet, Offer, etc.)
- **`scrapers/`**: Tests for web scrapers
- **`storage/`**: Tests for JSON storage and field filtering
- **`cli/`**: Tests for CLI commands
- **`utils/`**: Test utilities and helpers

---

## Running Tests

### Pre-Test Checklist

Before running tests, ensure code quality by running:

```bash
# Run linting (using uv - recommended)
uv run ruff check src/ tests/

# Auto-fix issues if any are found
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/
```

**Important**: Fix all ruff errors before running tests. Ruff catches issues that could cause test failures or mask real problems.

### Basic Commands

```bash
# Run all tests (using uv - recommended)
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run with HTML coverage report
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report

# Run in verbose mode
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Run with detailed output
uv run pytest -vv
```

### Running Specific Tests

```bash
# Run specific test file
uv run pytest tests/domain/test_entities.py

# Run specific test class
uv run pytest tests/domain/test_entities.py::TestShop

# Run specific test function
uv run pytest tests/domain/test_entities.py::TestShop::test_create_shop_with_all_fields

# Run tests matching a pattern
uv run pytest -k "shop"           # Tests containing "shop" in name
uv run pytest -k "validation"     # Tests containing "validation" in name
uv run pytest -k "shop or leaflet"  # Tests containing "shop" or "leaflet"
```

### Running Tests by Marker

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"

# Run unit tests that aren't slow
uv run pytest -m "unit and not slow"

# Run integration tests that aren't slow
uv run pytest -m "integration and not slow"
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
uv run pytest -n auto              # Auto-detect CPU cores
uv run pytest -n 4                 # Use 4 workers
```

### Debugging Tests

```bash
# Show local variables in tracebacks
uv run pytest -l

# Drop into debugger on failure
uv run pytest --pdb

# Debug test discovery
uv run pytest --collect-only -v

# Profile test execution time
uv run pytest --durations=10
```

---

## Test Organization

### Test Categories

Tests are organized into three main categories:

1. **Unit Tests** (`@pytest.mark.unit`)
   - Fast, isolated tests
   - No external dependencies
   - Test individual functions and methods
   - Located in `domain/`, `storage/`, and `scrapers/`

2. **Integration Tests** (`@pytest.mark.integration`)
   - Test how components work together
   - May use fixtures and mocks
   - Located in `scrapers/` and `cli/`

3. **Slow Tests** (`@pytest.mark.slow`)
   - Tests that take longer to run
   - May involve complex setup or teardown
   - Can be skipped during development

### Test Naming Conventions

- **Test files**: `test_*.py` or `*_test.py`
- **Test functions**: `def test_*()`
- **Test classes**: `class Test*`

Example:
```python
# tests/domain/test_shop.py

class TestShop:  # Test class
    def test_shop_creation(self):  # Test function
        pass
```

---

## Available Fixtures

### Built-in Fixtures (from conftest.py)

| Fixture | Description | Scope |
|---------|-------------|-------|
| `fixtures_dir` | Path to fixtures directory | function |
| `html_fixtures_dir` | Path to HTML fixtures directory | function |
| `test_config` | Test-specific Settings instance | session |
| `shops_html` | Shops page HTML fixture | function |
| `leaflet_html` | Leaflet page HTML fixture | function |
| `offer_html` | Offer page HTML fixture | function |
| `mock_driver` | Comprehensive mock Selenium WebDriver | function |
| `mock_wait` | Mock WebDriverWait and expected_conditions | function |
| `sample_shop_dict` | Sample shop data as dictionary | function |
| `sample_leaflet_dict` | Sample leaflet data as dictionary | function |

### Built-in Fixtures (from pytest)

| Fixture | Description |
|---------|-------------|
| `tmp_path` | Temporary directory for file I/O tests |
| `tmpdir` | Legacy temporary directory (use tmp_path instead) |

### Using Fixtures

Fixtures are automatically injected into test functions:

```python
def test_with_fixture(mock_driver, sample_shop_dict):
    """Test using shared fixtures."""
    # mock_driver is automatically injected
    # sample_shop_dict is automatically injected

    scraper = ShopScraper(mock_driver)
    shop = Shop.model_validate(sample_shop_dict)

    assert shop.slug == "biedronka"
```

### Creating Custom Fixtures

```python
import pytest
from pathlib import Path

@pytest.fixture
def custom_fixture(tmp_path):
    """Create a custom fixture."""
    # Setup
    test_file = tmp_path / "test.txt"
    test_file.write_text("test data")

    yield test_file  # Provide fixture to test

    # Teardown (if needed)
    # tmp_path is automatically cleaned up by pytest

def test_using_custom_fixture(custom_fixture):
    """Test using custom fixture."""
    assert custom_fixture.exists()
    assert custom_fixture.read_text() == "test data"
```

---

## Writing Tests

### The AAA Pattern

All tests must follow the **Arrange-Act-Assert (AAA)** pattern:

```python
def test_create_shop_with_all_fields(self, sample_shop_dict):
    """Test creating shop with all fields populated."""
    # Arrange: Set up test data and preconditions
    shop_data = sample_shop_dict.copy()

    # Act: Execute the code being tested
    shop = Shop.model_validate(shop_data)

    # Assert: Verify the outcome
    assert shop.slug == "biedronka"
    assert shop.brand_id == 23
    assert shop.name == "Biedronka"
    assert shop.leaflet_count == 13
    assert shop.is_popular is True
```

### Unit Test Example

```python
import pytest
from pydantic import ValidationError
from src.domain.entities import Shop


def test_shop_creation():
    """Test creating a Shop instance."""
    # Arrange
    shop_data = {
        "slug": "biedronka",
        "name": "Biedronka",
        "logo_url": "https://example.com/logo.png",
        "leaflet_count": 10,
        "is_popular": True
    }

    # Act
    shop = Shop.model_validate(shop_data)

    # Assert
    assert shop.slug == "biedronka"
    assert shop.name == "Biedronka"
    assert shop.leaflet_count == 10
    assert shop.is_popular is True


def test_shop_validation():
    """Test Shop validation."""
    # Arrange
    shop_data = {
        "slug": "",  # Empty slug should fail
        "name": "Test",
        "logo_url": "https://example.com/logo.png",
        "leaflet_count": 0
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        Shop.model_validate(shop_data)
```

### Integration Test Example

```python
import pytest
from bs4 import BeautifulSoup
from src.scrapers.shop_scraper import ShopScraper


def test_extract_shops(mock_driver, shops_html):
    """Test extracting shops from HTML."""
    # Arrange
    soup = BeautifulSoup(shops_html, 'lxml')

    # Act
    scraper = ShopScraper(mock_driver)
    shops = scraper._extract_entities(soup, "https://blix.pl/sklepy/")

    # Assert
    assert len(shops) > 0
    assert any(s.slug == "biedronka" for s in shops)
```

### Parametrized Test Example

```python
@pytest.mark.parametrize(
    "slug,should_fail",
    [
        ("valid-slug", False),
        ("valid_slug_123", False),
        ("UPPERCASE", False),
        ("", True),  # Empty string should fail
    ],
)
def test_shop_slug_validation(self, slug, should_fail, sample_shop_dict):
    """Test shop slug validation."""
    # Arrange
    shop_data = sample_shop_dict.copy()
    shop_data["slug"] = slug

    # Act & Assert
    if should_fail:
        with pytest.raises(ValidationError) as exc_info:
            Shop.model_validate(shop_data)
        assert "slug" in str(exc_info.value).lower()
    else:
        shop = Shop.model_validate(shop_data)
        assert shop.slug == slug
```

---

## Test Markers

### Available Markers

The project uses pytest markers to categorize tests:

```ini
# pytest.ini
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may use external services)
    slow: Slow-running tests
    scraping: Web scraping tests (may make network requests)
```

### Using Markers

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_integration_test():
    """Integration test."""
    pass

@pytest.mark.slow
def test_slow_test():
    """Slow test that takes time."""
    pass

@pytest.mark.unit
@pytest.mark.slow
def test_slow_unit_test():
    """Unit test that is slow."""
    pass
```

### Running Tests by Marker

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"

# Run unit tests that aren't slow
uv run pytest -m "unit and not slow"

# Run integration tests that aren't slow
uv run pytest -m "integration and not slow"
```

---

## Mocking Guidelines

### Mocking WebDriver

The project provides a comprehensive `mock_driver` fixture. Use it for all scraper tests:

```python
def test_scraper_with_mock_driver(mock_driver):
    """Test scraper with mocked WebDriver."""
    scraper = ShopScraper(mock_driver)

    # mock_driver.page_source is already set
    # mock_driver.get, mock_driver.quit are mocked
    # All common Selenium methods are mocked

    shops = scraper.scrape("https://blix.pl/sklepy/")
    assert len(shops) > 0
```

The `mock_driver` fixture includes:
- `page_source`: HTML content
- `get()`, `quit()`: Navigation methods
- `find_element()`, `find_elements()`: Element finding
- `switch_to`: Frame/window/alert switching
- `execute_script()`: JavaScript execution
- `current_url`, `title`: Page properties
- `cookies`: Cookie management

### Mocking External Dependencies

Use `unittest.mock.patch` to mock external dependencies:

```python
from unittest.mock import patch

@patch("src.cli.ScraperOrchestrator")
def test_cli_command(mock_orchestrator_class):
    """Test CLI command with mocked orchestrator."""
    # Arrange
    mock_orchestrator = mock_orchestrator_class.return_value
    mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
    mock_orchestrator.__exit__ = Mock(return_value=None)
    mock_orchestrator.scrape_all_shops.return_value = []

    # Act
    result = runner.invoke(app, ["scrape-shops"])

    # Assert
    assert result.exit_code == 0
    mock_orchestrator.scrape_all_shops.assert_called_once()
```

### Mocking Context Managers

When testing code that uses context managers:

```python
@patch("src.cli.ScraperOrchestrator")
def test_with_context_manager(mock_orchestrator_class):
    """Test code using context manager."""
    # Arrange
    mock_orchestrator = mock_orchestrator_class.return_value
    mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
    mock_orchestrator.__exit__ = Mock(return_value=None)

    # Act
    with mock_orchestrator:
        result = mock_orchestrator.scrape_all_shops()

    # Assert
    mock_orchestrator.__enter__.assert_called_once()
    mock_orchestrator.__exit__.assert_called_once()
```

---

## Examples

### Example 1: Testing Pydantic Entity

```python
# tests/domain/test_entities.py

class TestShop:
    def test_create_shop_with_all_fields(self, sample_shop_dict):
        """Test creating shop with all fields populated."""
        # Arrange
        shop_data = sample_shop_dict.copy()

        # Act
        shop = Shop.model_validate(shop_data)

        # Assert
        assert shop.slug == "biedronka"
        assert shop.brand_id == 23
        assert shop.name == "Biedronka"
        assert shop.leaflet_count == 13
        assert shop.is_popular is True
```

### Example 2: Testing Scraper

```python
# tests/scrapers/test_shop_scraper.py

def test_extract_shop_from_html(self, mock_driver):
    """Test extracting shop from HTML element."""
    # Arrange
    html = """
    <a href="/sklep/biedronka/" title="Biedronka">
        <div class="brand section-n__item">
            <img class="brand__logo" data-src="https://img.blix.pl/brand/23.jpg" />
        </div>
    </a>
    """

    soup = BeautifulSoup(html, 'lxml')
    brand_div = soup.select_one('.brand')

    # Act
    scraper = ShopScraper(mock_driver)
    shop = scraper._extract_shop(brand_div, is_popular=True)

    # Assert
    assert shop is not None
    assert shop.slug == "biedronka"
    assert shop.name == "Biedronka"
    assert shop.is_popular is True
```

### Example 3: Testing Storage

```python
# tests/storage/test_json_storage.py

def test_save_entity_creates_file(self, shop_storage, sample_shop_dict, tmp_path):
    """Test saving entity creates JSON file."""
    # Arrange
    shop = Shop.model_validate(sample_shop_dict)

    # Act
    filepath = shop_storage.save(shop, "biedronka.json")

    # Assert
    assert filepath == tmp_path / "biedronka.json"
    assert filepath.exists()
    assert filepath.is_file()
```

### Example 4: Testing CLI

```python
# tests/cli/test_cli.py

from typer.testing import CliRunner

runner = CliRunner()

@patch("src.cli.ScraperOrchestrator")
def test_scrape_shops_default_options(self, mock_orchestrator_class, sample_shops):
    """Test scrape-shops command with default options."""
    # Arrange
    mock_orchestrator = mock_orchestrator_class.return_value
    mock_orchestrator.__enter__ = Mock(return_value=mock_orchestrator)
    mock_orchestrator.__exit__ = Mock(return_value=None)
    mock_orchestrator.scrape_all_shops.return_value = sample_shops

    # Act
    result = runner.invoke(app, ["scrape-shops"])

    # Assert
    assert result.exit_code == 0
    mock_orchestrator_class.assert_called_once_with(headless=False)
    mock_orchestrator.scrape_all_shops.assert_called_once()
    assert "Scraped Shops" in result.stdout
    assert "Biedronka" in result.stdout
    assert "✓ Scraped 2 shops" in result.stdout
```

---

## Contribution Guidelines

### Adding New Tests

1. **Follow AAA pattern**: Arrange, Act, Assert
2. **Use descriptive names**: `test_shop_slug_validation` is better than `test_validation`
3. **Test one thing per test**: Each test should verify a single behavior
4. **Use fixtures**: Avoid code duplication with shared fixtures
5. **Mock external dependencies**: Don't make network calls in tests
6. **Test edge cases**: Test empty inputs, None values, invalid data
7. **Keep tests fast**: Unit tests should run in milliseconds
8. **Use markers**: Categorize tests with pytest markers

### Test Coverage

- **Minimum threshold**: 70% code coverage required
- **Critical paths**: 90%+ (authentication, data validation, storage)
- **New code**: Must meet 70% minimum before merging

### Code Review Checklist

- [ ] Tests follow AAA pattern
- [ ] Tests have descriptive names
- [ ] Tests use appropriate fixtures
- [ ] External dependencies are mocked
- [ ] Edge cases are tested
- [ ] Tests are fast (unless marked as slow)
- [ ] Tests have appropriate markers
- [ ] Coverage is maintained or improved

### Common Pitfalls

1. **Not mocking WebDriver**: Always use `mock_driver` fixture for scraper tests
2. **Testing implementation details**: Test behavior, not implementation
3. **Over-mocking**: Only mock what you need to isolate
4. **Not testing error cases**: Test how code handles invalid data
5. **Slow tests**: Mark slow tests with `@pytest.mark.slow`
6. **Test dependencies**: Tests should be independent
7. **Hardcoded values**: Use fixtures for test data
8. **Not cleaning up**: Use `tmp_path` for file I/O tests

### Troubleshooting

#### Test Discovery Issues

If pytest doesn't find your tests:

```bash
# Debug test discovery
uv run pytest --collect-only -v
```

#### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Install with uv (recommended)
uv sync

# Or install in editable mode with pip
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

#### Fixture Not Found

If a fixture isn't found:

```bash
# Check fixture is defined in conftest.py or test file
# Check fixture name matches exactly (case-sensitive)
# Check fixture is in the correct scope
```

#### Slow Tests

If tests are running slowly:

```bash
# Run only unit tests (skip integration and slow tests)
uv run pytest -m "unit and not slow"

# Run tests in parallel
uv run pytest -n auto

# Profile test execution time
uv run pytest --durations=10
```

---

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Parametrize](https://docs.pytest.org/en/stable/parametrize.html)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Project Testing Best Practices](../.specify/memory/testing-best-practices.md)
- [Developer Guide](../docs/developer-guide.md)
