# Quick Start: Running Tests

**Feature**: Improve Testing Infrastructure  
**Created**: 2026-01-16

## Installation

```bash
# Install project with test dependencies
uv pip install -e .[test]

# Or install separately
uv pip install pytest pytest-cov pytest-mock
```

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=src --cov-report=xml
```

### Specific Test Types

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# Run specific test file
pytest tests/unit/test_entities.py

# Run specific test
pytest tests/unit/test_entities.py::TestShop::test_create_shop
```

### Verbose Output

```bash
# Detailed output
pytest -v

# Show captured stdout/stderr
pytest -s

# Debug traceback
pytest --tb=short
pytest --tb=long
pytest --pdb  # Enter debugger on failure
```

## Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=term-missing --cov-fail-under=70

[coverage:run]
source = src
omit = */tests/* */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

## CI/CD

### GitHub Actions

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main`

Manual trigger:
```bash
# View workflow status
gh run list --workflow=test.yml
```

### Local CI Simulation

```bash
# Run same commands as CI
pytest --cov=src --cov-report=xml --cov-report=term-missing
```

## Writing Tests

### Basic Test Structure

```python
# tests/unit/test_example.py

import pytest
from src.example import ExampleClass

class TestExampleClass:
    """Test cases for ExampleClass."""
    
    def test_create_instance(self):
        """Test that instance is created correctly."""
        # Arrange
        name = "test"
        
        # Act
        instance = ExampleClass(name)
        
        # Assert
        assert instance.name == name
    
    def test_method_behavior(self):
        """Test specific method behavior."""
        instance = ExampleClass("test")
        result = instance.method()
        assert result is not None
    
    @pytest.mark.parametrize("input,expected", [
        ("a", "A"),
        ("b", "B"),
    ])
    def test_parametrized(self, input, expected):
        """Test with multiple inputs."""
        instance = ExampleClass(input)
        result = instance.method()
        assert result == expected
```

### Using Fixtures

```python
# tests/conftest.py

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_driver():
    """Mock WebDriver for scraping tests."""
    driver = MagicMock()
    driver.page_source = "<html>Test</html>"
    return driver

# In test file
def test_scraper_parsing(mock_driver):
    from src.scrapers import ShopScraper
    scraper = ShopScraper()
    scraper.driver = mock_driver
    result = scraper.scrape()
    assert result is not None
```

## Test Coverage Goals

| Metric | Current | Target |
|--------|---------|--------|
| Line Coverage | 0% | 70% |
| Function Coverage | 0% | 80% |
| Branch Coverage | 0% | 60% |

## Troubleshooting

### Tests Not Found

```bash
# Check test discovery
pytest --collect-only

# Ensure files are named test_*.py
# Ensure classes are named Test*
# Ensure functions are named test_*
```

### Coverage Not Meeting Threshold

```bash
# See which lines are not covered
pytest --cov=src --cov-report=term-missing

# Generate HTML to see uncovered lines
pytest --cov=src --cov-report=html
```

### Slow Tests

```bash
# Identify slow tests
pytest --durations=10

# Run only fast tests
pytest -m "not slow"
```

## Best Practices

1. **Follow AAA Pattern**: Arrange → Act → Assert
2. **Keep Tests Isolated**: No test should depend on another
3. **Use Fixtures**: Reusable setup code
4. **Parametrize Tests**: Avoid duplication
5. **Mock External Dependencies**: Don't make real network calls
6. **Meaningful Names**: Test names should describe what they verify
