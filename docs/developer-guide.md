---
title: Developer Guide
description: Guide for contributing to blix-scraper
category: documentation
tags:
  - developer-guide
  - contributing
  - development
  - testing
created: 2026-01-16
updated: 2026-01-16
---

# Developer Guide

Guide for contributing to the blix-scraper project.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Contributing](#contributing)
8. [Building and Releasing](#building-and-releasing)

---

## Project Overview

### Purpose

Blix-scraper is a web scraping tool for extracting promotional leaflet data from blix.pl. It allows users to:

- Extract shop information (brands, categories)
- Scrape promotional leaflets with validity dates
- Extract product offers with prices and positions
- Capture keywords and categories
- Search products across all shops

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| WebDriver | `undetected-chromedriver` | Bypasses anti-bot detection |
| HTML Parsing | `BeautifulSoup4` + `lxml` | Robust HTML parsing |
| Data Validation | `Pydantic v2` | Type safety and validation |
| CLI Interface | `Typer` + `Rich` | Modern CLI with rich output |
| Logging | `structlog` | Structured logging |
| Testing | `pytest` | Unit and integration testing |

### Key Design Principles

1. **Simplicity**: File-based storage (no database complexity)
2. **Separation of Concerns**: Scrapers, storage, orchestration are independent
3. **Testability**: Real HTML fixtures for testing
4. **Robustness**: Undetected Chrome handles anti-bot measures
5. **Single Responsibility**: Each scraper handles one entity type

---

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Google Chrome browser
- Code editor (VS Code recommended)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/blix-scraper
   cd blix-scraper
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Install pre-commit hooks** (if configured):
   ```bash
   pre-commit install
   ```

5. **Verify installation**:
   ```bash
   python -m src.cli --help
   ```

### IDE Configuration

#### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- Ruff
- GitLens

Settings (`settings.json`):
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "editor.formatOnSave": true,
  "python.formatting.provider": "black",
  "python.linting.ruffEnabled": true,
  "python.linting.ruffArgs": ["--fix"]
}
```

#### PyCharm

1. Open project directory
2. Set Python interpreter to `./venv/bin/python`
3. Enable Black as formatter
4. Configure Ruff as linter

---

## Project Structure

```
blix-scraper/
├── src/                      # Source code
│   ├── cli/                  # CLI interface
│   ├── domain/               # Domain entities (Pydantic models)
│   ├── scrapers/             # Web scrapers
│   ├── storage/              # Data storage
│   ├── webdriver/            # WebDriver management
│   ├── config.py             # Configuration
│   ├── logging_config.py     # Logging setup
│   └── orchestrator.py       # Workflow orchestration
├── tests/                    # Test suite
│   ├── fixtures/             # Test data
│   │   ├── html/             # HTML fixtures
│   │   └── json/             # JSON fixtures
│   ├── domain/               # Domain tests
│   ├── scrapers/             # Scraper tests
│   └── storage/              # Storage tests
├── examples/                 # Example scripts
├── docs/                     # Documentation
├── data/                     # Scraped data (gitignored)
├── logs/                     # Application logs
├── .env.example              # Environment template
├── pyproject.toml            # Project configuration
├── requirements.txt          # Dependencies
└── README.md                 # Project README
```

### Key Files

| File | Purpose |
|------|---------|
| `src/orchestrator.py` | Main orchestration class |
| `src/config.py` | Configuration management |
| `src/domain/entities.py` | Pydantic data models |
| `src/scrapers/base.py` | Base scraper class |
| `src/storage/json_storage.py` | JSON file storage |

---

## Coding Standards

### Code Style

Follow these standards:

1. **Formatting**: Black (line length: 88)
2. **Linting**: Ruff
3. **Type Checking**: MyPy (strict mode)
4. **Imports**: Ruff import sorting

### Style Guide

#### Python Code

```python
"""Module docstring."""

from typing import List, Optional
from pathlib import Path

import structlog

from src.domain.entities import Shop
from src.storage.json_storage import JSONStorage


class ExampleClass:
    """
    Class docstring.

    Attributes:
        attribute: Description of attribute.
    """

    def __init__(self, name: str, value: Optional[int] = None) -> None:
        """Initialize the class."""
        self.name = name
        self.value = value

    def process(self, data: List[str]) -> dict:
        """
        Process data and return result.

        Args:
            data: List of strings to process.

        Returns:
            Dictionary with results.
        """
        result = {"count": len(data), "items": data}
        return result
```

#### Documentation

```python
def function_name(param: Type) -> ReturnType:
    """
    Short description of function.

    Longer description if needed. Can span multiple lines.

    Args:
        param: Description of parameter.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When this exception is raised.

    Example:
        >>> function_name("example")
        {'result': 'example'}
    """
    pass
```

#### Git Commits

Follow conventional commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance

Examples:
```
feat(scraper): Add new shop scraper for Lidl
fix(orchestrator): Handle empty leaflet list
docs(readme): Update installation instructions
test(entity): Add tests for Shop model
```

---

## Testing

### Running Tests

The project uses pytest for testing. Here are the most common commands:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run with HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report

# Run specific test file
pytest tests/domain/test_entities.py

# Run specific test
pytest tests/domain/test_entities.py::TestShop::test_create_shop_with_all_fields

# Run in verbose mode
pytest -v

# Stop on first failure
pytest -x

# Run tests matching a pattern
pytest -k "shop"           # Tests containing "shop" in name
pytest -k "validation"     # Tests containing "validation" in name

# Run by marker
pytest -m unit              # Only unit tests (fast, no external dependencies)
pytest -m integration       # Only integration tests (may use external services)
pytest -m "not slow"        # Skip slow tests
pytest -m "unit and not slow"  # Unit tests that aren't slow

# Run tests in parallel (requires pytest-xdist)
pytest -n auto              # Auto-detect CPU cores
pytest -n 4                 # Use 4 workers

# Show local variables in tracebacks
pytest -l

# Run with detailed output
pytest -vv
```

### Test Structure

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

### Writing Tests

#### The AAA Pattern

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

#### Unit Tests

Unit tests are fast, isolated tests that test individual functions or methods:

```python
# tests/domain/test_shop.py
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

#### Integration Tests

Integration tests test how multiple components work together:

```python
# tests/scrapers/test_shop_scraper.py
import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from src.scrapers.shop_scraper import ShopScraper


@pytest.fixture
def sample_html():
    """Load sample HTML for testing."""
    fixture_path = Path(__file__).parent.parent / "fixtures/html/shops_page.html"
    return fixture_path.read_text()


def test_extract_shops(sample_html, mock_driver):
    """Test extracting shops from HTML."""
    # Arrange
    soup = BeautifulSoup(sample_html, 'lxml')

    # Act
    scraper = ShopScraper(mock_driver)
    shops = scraper._extract_entities(soup, "https://blix.pl/sklepy/")

    # Assert
    assert len(shops) > 0
    assert any(s.slug == "biedronka" for s in shops)
```

### Test Fixtures

#### Available Fixtures

The project provides several shared fixtures in `tests/conftest.py`:

- `fixtures_dir`: Path to fixtures directory
- `html_fixtures_dir`: Path to HTML fixtures directory
- `test_config`: Test-specific Settings instance
- `shops_html`: Shops page HTML fixture
- `leaflet_html`: Leaflet page HTML fixture
- `offer_html`: Offer page HTML fixture
- `mock_driver`: Comprehensive mock Selenium WebDriver
- `mock_wait`: Mock WebDriverWait and expected_conditions
- `sample_shop_dict`: Sample shop data as dictionary
- `sample_leaflet_dict`: Sample leaflet data as dictionary
- `tmp_path`: pytest's built-in temporary directory fixture

#### Using Fixtures

```python
def test_with_fixture(mock_driver, sample_shop_dict):
    """Test using shared fixtures."""
    # mock_driver is automatically injected
    # sample_shop_dict is automatically injected

    scraper = ShopScraper(mock_driver)
    shop = Shop.model_validate(sample_shop_dict)

    assert shop.slug == "biedronka"
```

#### Creating Custom Fixtures

```python
@pytest.fixture
def custom_fixture(tmp_path):
    """Create a custom fixture."""
    # Setup
    test_file = tmp_path / "test.txt"
    test_file.write_text("test data")

    yield test_file  # Provide fixture to test

    # Teardown (if needed)
    # tmp_path is automatically cleaned up by pytest
```

### Test Markers

The project uses pytest markers to categorize tests:

```ini
# pytest.ini
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may use external services)
    slow: Slow-running tests
    scraping: Web scraping tests (may make network requests)
```

#### Using Markers

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
```

#### Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run unit tests that aren't slow
pytest -m "unit and not slow"
```

### Parametrization

Test multiple scenarios with a single test function:

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
        with pytest.raises(ValidationError):
            Shop.model_validate(shop_data)
    else:
        shop = Shop.model_validate(shop_data)
        assert shop.slug == slug
```

### Mocking Guidelines

#### Mocking WebDriver

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

#### Mocking External Dependencies

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

#### Mocking Context Managers

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

### Test Fixtures

#### HTML Fixtures

The project uses real HTML fixtures captured from blix.pl:

```bash
# Capture HTML for testing
python -m tests.utils.capture_html \
    --url https://blix.pl/sklepy/ \
    --output tests/fixtures/html/shops_page.html
```

#### Using HTML Fixtures

```python
@pytest.fixture
def shops_html(html_fixtures_dir) -> str:
    """Load shops page HTML fixture."""
    fixture_path = html_fixtures_dir / "shops_page.html"

    if fixture_path.exists():
        return fixture_path.read_text(encoding="utf-8")

    # Return minimal HTML if fixture not available
    return "<html><body>...</body></html>"
```

### Code Coverage

#### Generating Coverage Reports

```bash
# Generate terminal coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Generate XML coverage report (for CI/CD)
pytest --cov=src --cov-report=xml
```

#### Coverage Goals

- **Overall coverage**: 80%+
- **Critical paths**: 90%+ (authentication, data validation, storage)
- **New code**: 80%+ before merging

#### Coverage Configuration

```ini
# pytest.ini
[pytest]
addopts = --cov=src --cov-report=term-missing
```

### Troubleshooting

#### Test Discovery Issues

If pytest doesn't find your tests:

```bash
# Debug test discovery
pytest --collect-only -v

# Check naming conventions:
# - Test files: test_*.py or *_test.py
# - Test functions: def test_*()
# - Test classes: class Test*
```

#### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Install package in editable mode
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
pytest -m "unit and not slow"

# Run tests in parallel
pytest -n auto

# Profile test execution time
pytest --durations=10
```

### Best Practices

1. **Follow AAA pattern**: Arrange, Act, Assert - makes tests readable and maintainable
2. **Use descriptive test names**: `test_shop_slug_validation` is better than `test_validation`
3. **Test one thing per test**: Each test should verify a single behavior
4. **Use fixtures for setup**: Avoid code duplication with shared fixtures
5. **Mock external dependencies**: Don't make network calls in tests
6. **Test edge cases**: Test empty inputs, None values, invalid data
7. **Keep tests fast**: Unit tests should run in milliseconds
8. **Use markers**: Categorize tests with pytest markers
9. **Maintain high coverage**: Aim for 80%+ coverage
10. **Test error handling**: Don't just test happy paths

---

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and automated testing. The CI pipeline ensures code quality, test coverage, and cross-platform compatibility.

### Workflow Overview

The CI workflow is defined in `.github/workflows/test.yml` and runs on every push and pull request to the `main` and `develop` branches.

#### Workflow Triggers

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

The workflow automatically runs when:
- Code is pushed to `main` or `develop` branches
- A pull request is created targeting `main` or `develop`
- Pull requests are updated with new commits

#### Test Matrix

The workflow tests across multiple operating systems and Python versions:

| OS | Python Version | Purpose |
|----|----------------|---------|
| Ubuntu Latest | 3.11 | Linux compatibility |
| Windows Latest | 3.11 | Windows compatibility |
| macOS Latest | 3.11 | macOS compatibility |

This matrix ensures the code works consistently across all major platforms.

#### Workflow Steps

1. **Checkout Code**
   ```yaml
   - name: Checkout code
     uses: actions/checkout@v4
   ```
   Retrieves the repository code.

2. **Set up Python**
   ```yaml
   - name: Set up Python ${{ matrix.python-version }}
     uses: actions/setup-python@v5
   ```
   Installs the specified Python version.

3. **Install Poetry**
   ```yaml
   - name: Install Poetry
     uses: snok/install-poetry@v1
   ```
   Sets up Poetry for dependency management.

4. **Cache Dependencies**
   ```yaml
   - name: Load cached venv
     uses: actions/cache@v4
   ```
   Caches the virtual environment to speed up subsequent runs.

5. **Install Dependencies**
   ```yaml
   - name: Install dependencies
     run: poetry install --with dev
   ```
   Installs project dependencies including dev tools.

6. **Run Tests with Coverage**
   ```yaml
   - name: Run tests with coverage
     run: |
       poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=70
   ```
   Executes tests with coverage reporting and enforces 70% minimum coverage.

7. **Upload Coverage to Codecov**
   ```yaml
   - name: Upload coverage to Codecov
     uses: codecov/codecov-action@v3
   ```
   Uploads coverage reports to Codecov for historical tracking.

8. **Upload Coverage Artifacts**
   ```yaml
   - name: Upload coverage artifacts
     uses: actions/upload-artifact@v4
   ```
   Uploads coverage reports as GitHub artifacts for download.

### Coverage Gate

The CI pipeline enforces a **70% minimum code coverage** requirement using the `--cov-fail-under=70` flag.

#### Coverage Requirements

- **Minimum Threshold**: 70% code coverage
- **Failure Condition**: Build fails if coverage drops below 70%
- **Reports Generated**:
  - Terminal report: Shows missing lines during CI run
  - XML report: Uploaded to Codecov for tracking
  - HTML report: Available as downloadable artifact

#### Checking Coverage Locally

Before pushing changes, verify coverage locally:

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=70

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View in browser
```

#### Improving Coverage

If coverage is below 70%:

1. Identify uncovered code:
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

2. Review the missing lines in the terminal output

3. Add tests for uncovered code paths

4. Re-run tests to verify improvement

### Artifacts

The workflow uploads coverage reports as artifacts for each run:

#### Artifact Details

- **Name**: `coverage-{run_id}-{os}`
- **Contents**:
  - `coverage.xml`: XML coverage report
  - `htmlcov/`: HTML coverage report directory
- **Retention**: 30 days
- **Availability**: Downloadable from the Actions tab

#### Accessing Artifacts

1. Navigate to the Actions tab in GitHub
2. Click on a workflow run
3. Scroll to the "Artifacts" section
4. Download the coverage artifact for your OS

### Workflow Timeout

The test job has a 15-minute timeout to prevent hung jobs from consuming CI resources:

```yaml
timeout-minutes: 15
```

If a job exceeds this limit, it will be automatically cancelled.

### Running CI Checks Locally

To replicate the CI environment locally:

#### Using Poetry

```bash
# Install dependencies
poetry install --with dev

# Run tests with same flags as CI
poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=70

# Run linting
poetry run ruff check src/ tests/

# Run type checking
poetry run mypy src/
```

#### Using pip

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov ruff mypy

# Run tests
pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=70

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/
```

### Troubleshooting CI Failures

#### Test Failures

**Symptoms**: Tests pass locally but fail in CI

**Common Causes**:
1. Platform-specific code (Windows vs Linux)
2. Different dependency versions
3. Environment differences

**Solutions**:
1. Check the specific OS that failed in the matrix
2. Review test logs for platform-specific issues
3. Ensure dependencies are pinned in `pyproject.toml`
4. Test locally on the failing platform if possible

#### Coverage Failures

**Symptoms**: Coverage below 70% threshold

**Solutions**:
1. Download coverage artifact to see detailed report
2. Identify uncovered lines in the HTML report
3. Add tests for uncovered code paths
4. Verify coverage locally before pushing

#### Timeout Failures

**Symptoms**: Job exceeds 15-minute timeout

**Solutions**:
1. Check for infinite loops or slow operations
2. Optimize test execution time
3. Use mocking for slow external dependencies
4. Split large test files into smaller ones

#### Dependency Installation Failures

**Symptoms**: Poetry install fails

**Solutions**:
1. Check `poetry.lock` is committed
2. Verify `pyproject.toml` is valid
3. Clear cache: `poetry cache clear --all pypi`
4. Update Poetry version if needed

#### Codecov Upload Failures

**Symptoms**: Codecov action fails

**Solutions**:
1. For private repos: Add `CODECOV_TOKEN` secret
2. For public repos: Ensure repo is public on Codecov
3. Check network connectivity
4. Verify `coverage.xml` was generated

### Required Secrets

For private repositories, configure the following secret in GitHub repository settings:

#### CODECOV_TOKEN

**Purpose**: Authenticate with Codecov for private repositories

**Setup**:
1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Get your upload token
4. Navigate to: Repository Settings → Secrets and variables → Actions
5. Click "New repository secret"
6. Name: `CODECOV_TOKEN`
7. Value: Your Codecov token

**Note**: Public repositories don't require a token.

### Best Practices

#### Before Pushing

1. **Run full test suite**:
   ```bash
   pytest --cov=src --cov-fail-under=70
   ```

2. **Run linting**:
   ```bash
   ruff check src/ tests/
   ```

3. **Run type checking**:
   ```bash
   mypy src/
   ```

4. **Format code**:
   ```bash
   black src/ tests/
   ```

#### During Development

1. **Write tests first** (TDD approach)
2. **Keep coverage above 70%** at all times
3. **Test on multiple platforms** if possible
4. **Use meaningful commit messages**

#### Pull Request Workflow

1. Create feature branch from `develop`
2. Make changes and commit
3. Push to your fork
4. Create pull request
5. CI runs automatically
6. Address any failures
7. Request review
8. Merge after approval and passing CI

### Monitoring CI Status

#### Workflow Badge

Add the CI status badge to your README:

```markdown
![Tests](https://github.com/seszele64/blix-scraper/workflows/Tests/badge.svg)
```

This badge shows the current status of the main branch.

#### Viewing Workflow Runs

1. Navigate to the Actions tab in GitHub
2. View recent workflow runs
3. Click on a run to see details
4. Check logs for each step
5. Download artifacts if needed

### CI/CD Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)

---

## Contributing

### Workflow

1. **Fork the repository** on GitHub
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following coding standards
4. **Add tests** for your changes
5. **Run tests** to ensure everything passes
6. **Commit changes** with clear messages
7. **Push to your fork**
8. **Create a pull request**

### Pull Request Guidelines

1. **Title**: Clear, descriptive title
2. **Description**: Explain what changed and why
3. **Checklist**:
   - [ ] Code follows style guidelines
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] All tests pass
   - [ ] No linting errors

### Code Review

Expect feedback on:
- Code clarity and readability
- Test coverage
- Documentation completeness
- Edge case handling
- Performance implications

### Bug Reports

When reporting bugs:

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template**
3. **Include**:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Error messages
   - Environment details

### Feature Requests

When requesting features:

1. **Check existing requests** to avoid duplicates
2. **Describe the use case** clearly
3. **Explain why** this feature is valuable
4. **Suggest implementation** if possible

---

## Building and Releasing

### Version Management

This project uses semantic versioning:

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

Version format: `MAJOR.MINOR.PATCH`

### Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md**
3. **Create release commit**
4. **Create GitHub release**
5. **Publish to PyPI** (if applicable)

### Building Documentation

```bash
# Build HTML documentation
mkdocs build

# Serve locally
mkdocs serve
```

### Pre-release Checklist

- [ ] All tests pass
- [ ] Code coverage maintained
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] No linting errors
- [ ] Type checking passes

---

## Additional Resources

### Related Documentation

- [User Guide](user-guide.md) - End-user documentation
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - System architecture
- [Domain Model](domain-model.md) - Data model documentation

### External Resources

- [Python Documentation](https://docs.python.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pytest Documentation](https://docs.pytest.org/)

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community discussion
- **Code Comments**: Inline documentation in source code
