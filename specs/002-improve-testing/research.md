# Research: Testing Best Practices for blix-scraper

**Feature**: Improve Testing Infrastructure  
**Created**: 2026-01-16  
**Source**: `docs/testing-best-practices.md`, industry standards

## Testing Framework Selection

### Decision: pytest

| Framework | Pros | Cons |
|-----------|------|------|
| **pytest** | Simple assert syntax, auto-discovery, extensive plugins | Requires learning fixtures |
| **unittest** | Built-in, no dependencies | Verbose, Java-style |
| **doctest** | Documentation integration | Limited for complex scenarios |

**Rationale**: pytest is the de facto standard for Python testing, offers minimal boilerplate, and has excellent plugin ecosystem (pytest-cov, pytest-mock, pytest-asyncio).

## Test Organization Patterns

### Test Pyramid Application

```
                    ┌─────────────────┐
                    │  End-to-End     │  5-10% - CI integration tests
                    │  Tests          │
                    ├─────────────────┤
                    │  Integration    │  15-25% - Component interactions
                    │  Tests          │
                    ├─────────────────┤
                    │    Unit Tests   │  70-80% - Fast, isolated tests
                    │                 │
                    └─────────────────┘
```

### Directory Structure

```text
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_entities.py
│   ├── test_json_storage.py
│   └── test_field_filter.py
├── integration/             # Integration tests (slower)
│   └── __init__.py
└── scrapers/                # Domain-specific tests
    └── test_shop_scraper.py
```

## Fixture Strategy

### Fixture Scopes

| Scope | Use Case | Example |
|-------|----------|---------|
| `function` | Per-test setup | temp_dir, mock_data |
| `class` | Per-class setup | logged_in_user |
| `module` | Per-module setup | test_database |
| `session` | Per-session setup | expensive_resource |

### Recommended Fixtures

```python
@pytest.fixture(scope="session")
def test_config():
    """Test configuration loaded from environment."""
    return {"base_url": "https://test.blix.pl"}

@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs."""
    yield tmp_path
    # Cleanup automatic via tmp_path

@pytest.fixture
def mock_driver():
    """Mock Selenium WebDriver for scraping tests."""
    with patch('selenium.webdriver.Chrome') as mock:
        yield mock
```

## Coverage Configuration

### pytest-cov Settings

```ini
# pytest.ini
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

### Coverage Goals

| Metric | Target | Measurement |
|--------|--------|-------------|
| Line Coverage | 70% | pytest-cov |
| Branch Coverage | 60% | pytest-cov |
| Function Coverage | 80% | pytest-cov |

## CI/CD Pipeline Design

### GitHub Actions Workflow

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          uv pip install -e . pytest pytest-cov pytest-mock
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term-missing
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false
```

## Mocking Strategy for Scrapers

### Web Scraping Test Patterns

```python
# Strategy 1: Mock download method
@patch.object(Scraper, 'download')
def test_parse_method(mock_download):
    mock_download.return_value = sample_html
    results = scraper.scrape()
    assert len(results) > 0

# Strategy 2: Use fixtures with pre-captured HTML
@pytest.fixture
def sample_shop_html():
    with open('tests/fixtures/shop_page.html') as f:
        return f.read()

def test_shop_parsing(sample_shop_html):
    soup = BeautifulSoup(sample_shop_html, 'html.parser')
    shop = parse_shop(soup)
    assert shop.name == "Test Shop"

# Strategy 3: Selenium Wire for full testing
from seleniumwire import webdriver

@pytest.fixture
def intercepted_driver():
    driver = webdriver.Chrome()
    driver.request_interceptor = mock_interceptor
    return driver
```

## Test Naming Conventions

| Pattern | Example | Purpose |
|---------|---------|---------|
| `test_<module>_<function>` | `test_json_storage_save` | Identify tested unit |
| `Test<class>` | `TestJSONStorage` | Group related tests |
| `test_<scenario>_<expected>` | `test_save_valid_data_succeeds` | Describe behavior |

## Best Practices Summary

### Do's

- ✅ Follow AAA pattern (Arrange-Act-Assert)
- ✅ Use fixtures for reusable setup
- ✅ Mock external dependencies
- ✅ Parametrize similar tests
- ✅ Keep tests fast and isolated
- ✅ Use meaningful test names
- ✅ Aim for 70%+ coverage on critical paths

### Don'ts

- ❌ Don't depend on test execution order
- ❌ Don't share state between tests
- ❌ Don't make network calls in unit tests
- ❌ Don't test implementation details
- ❌ Don't write brittle tests

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Hypothesis for property testing | Overkill for this project size |
| Selenium Wire for all tests | Too slow, use mocking instead |
| Separate coverage tool | pytest-cov is sufficient |
| tox for multi-Python testing | GitHub Actions matrix is simpler |

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](docs/testing-best-practices.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
