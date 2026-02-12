---
title: Testing Best Practices
description: Comprehensive guide to testing Python applications with pytest, including general testing principles and web scraping-specific strategies
type: note
relationships:
  relates_to:
    - implementation-patterns.md
    - developer-guide.md
tags:
  - testing
  - pytest
  - best-practices
  - tdd
  - fixtures
  - mocking
  - selenium
  - web-scraping
created: 2026-01-16
updated: 2026-01-16
version: 1.0.0
---

# Testing Best Practices

This document provides comprehensive guidance on testing Python applications, with special focus on pytest and web scraping testing strategies.

## Core Testing Principles

### The AAA Pattern: Arrange-Act-Assert

Every well-structured test follows three distinct phases:

```python
import pytest
from calculator import Calculator

def test_division_with_positive_numbers():
    # Arrange: Set up test data and preconditions
    calc = Calculator()
    dividend = 10
    divisor = 2
    
    # Act: Execute the code being tested
    result = calc.divide(dividend, divisor)
    
    # Assert: Verify the outcome
    assert result == 5.0
```

This pattern improves readability and makes test failures easier to diagnose. Each section has a clear purpose, making tests self-documenting.

### Test Isolation and Independence

Tests must be completely independent—no test should rely on another test's execution or state:

```python
import pytest

class TestUserAccount:
    def test_user_creation(self):
        # Each test starts fresh
        user = User("alice@example.com")
        assert user.email == "alice@example.com"

    def test_user_deletion(self):
        # This test doesn't depend on test_user_creation
        user = User("bob@example.com")
        user.delete()
        assert user.is_deleted is True
```

Violating test isolation leads to flaky tests that pass or fail based on execution order.

## pytest Fundamentals

### pytest vs unittest

| Feature | pytest | unittest |
|---------|--------|----------|
| Syntax | Plain `assert` statements | Special assertion methods |
| Boilerplate | Minimal | More verbose |
| Discovery | Automatic by naming convention | Requires TestCase inheritance |
| Plugins | Extensive ecosystem | Limited |
| Popularity | De facto standard | Built-in alternative |

### Naming Conventions

pytest follows these conventions for test discovery:
- Test files: `test_*.py` or `*_test.py`
- Test functions: `def test_*()`
- Test classes: `class Test*`

### Basic pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --cov=src --cov-report=term-missing
```

## pytest Fixtures

### Creating Reusable Fixtures

Fixtures eliminate code duplication and provide clean setup/teardown:

```python
import pytest
from database import Database

@pytest.fixture
def db_connection():
    """Provide a database connection for testing."""
    # Setup: Create connection
    db = Database("test.db")
    db.connect()
    yield db  # Provide fixture to test
    # Teardown: Clean up
    db.disconnect()
    db.remove()

def test_user_insert(db_connection):
    # db_connection fixture automatically injected
    user_id = db_connection.insert_user("Alice", "alice@test.com")
    assert user_id is not None
    assert db_connection.get_user(user_id)["name"] == "Alice"
```

### Fixture Scopes

Fixture scopes control how often fixtures are created:

| Scope | Description |
|-------|-------------|
| `function` (default) | New instance per test |
| `class` | Shared across test class |
| `module` | Shared across module |
| `session` | Created once for entire test run |

```python
@pytest.fixture(scope="session")
def database_schema():
    """Initialize database schema once for all tests."""
    db = Database(":memory:")
    db.create_tables()
    return db
```

## Parametrization

### Basic Parametrization

Test multiple inputs efficiently without duplicating code:

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    (0, 0),           # Zero case
    (1, 1),           # Base case
    (5, 120),         # Typical case
    (10, 3628800),    # Larger number
])
def test_factorial(input_value, expected):
    from math_utils import factorial
    assert factorial(input_value) == expected

@pytest.mark.parametrize("invalid_input", [
    -1,     # Negative number
    1.5,    # Float
    "five", # String
    None,   # None value
])
def test_factorial_invalid_input(invalid_input):
    from math_utils import factorial
    with pytest.raises(ValueError):
        factorial(invalid_input)
```

### Multiple Parameters

```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_addition(a, b, expected):
    assert add(a, b) == expected
```

## Mocking External Dependencies

### Using unittest.mock

Isolate code from external services, databases, or APIs:

```python
from unittest.mock import patch, MagicMock
import pytest
import requests

def fetch_user_data(user_id):
    """Fetch user data from external API."""
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

@patch("requests.get")
def test_fetch_user_data_success(mock_get):
    # Arrange: Configure mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 123,
        "name": "Alice",
        "email": "alice@example.com"
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Act: Call function with mocked dependency
    result = fetch_user_data(123)
    
    # Assert: Verify behavior
    assert result["name"] == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/123")

@patch("requests.get")
def test_fetch_user_data_api_error(mock_get):
    # Simulate API failure
    mock_get.side_effect = requests.RequestException("API unavailable")
    with pytest.raises(requests.RequestException):
        fetch_user_data(123)
```

**Key Mocking Principle**: Patch where the object is used, not where it's defined.

## Web Scraping Testing Strategies

### The Scraper Architecture Pattern

Structure scrapers with separable methods for testability:

```python
class BooksScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
    
    def __del__(self):
        self.driver.quit()
    
    def download(self, url: str) -> str:
        """Retrieve HTML content."""
        self.driver.get(url)
        return self.driver.page_source
    
    def parse(self, html: str) -> list:
        """Extract data from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        return [a.get("href") for a in soup.select("h3 > a", href=True)]
    
    def transform(self, links: list) -> pl.DataFrame:
        """Create structured data."""
        return pl.DataFrame({"url": links})
```

### Strategy 1: Mocking the Download Method

The simplest approach—mock the entire download method:

```python
import pytest
from unittest.mock import MagicMock
import polars as pl
from scraper import BooksScraper

URL = "https://books.toscrape.com/"
LINKS = pl.read_csv("books-to-scrape.csv")

@pytest.fixture
def scraper():
    bs = BooksScraper()
    with open("books-to-scrape.html", "r") as f:
        # Mock the download() method, loading HTML from file
        bs.download = MagicMock(return_value=f.read())
    return bs

def test_scraper(scraper):
    html = scraper.download(URL)
    links = scraper.parse(html)
    assert links == LINKS["url"].to_list()
    df = scraper.transform(links)
    assert df.equals(LINKS)
```

### Strategy 2: Patching with patch.object

```python
import pytest
from unittest.mock import patch
import polars as pl
from scraper import BooksScraper

URL = "https://books.toscrape.com/"
LINKS = pl.read_csv("books-to-scrape.csv")

@pytest.fixture
def scraper():
    return BooksScraper()

@patch.object(BooksScraper, "download")
def test_scraper(patched_download, scraper):
    with open("books-to-scrape.html", "r") as f:
        patched_download.return_value = f.read()
    
    html = scraper.download(URL)
    links = scraper.parse(html)
    assert links == LINKS["url"].to_list()
    df = scraper.transform(links)
    assert df.equals(LINKS)
```

### Strategy 3: Selenium Wire Request Interception

For more complete testing including Selenium code, use Selenium Wire:

```python
from seleniumwire import webdriver
import pytest
import polars as pl
from scraper import BooksScraper

URL = "https://books.toscrape.com/"
LINKS = pl.read_csv("books-to-scrape.csv")

@pytest.fixture
def mock_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    with open("books-to-scrape.html") as f:
        MOCK_RESPONSE = f.read()
    
    def interceptor(request):
        if request.url == URL:
            # Intercept the request and return mock response
            request.create_response(
                status_code=200,
                headers={"Content-Type": "text/html"},
                body=MOCK_RESPONSE.encode("utf-8"),
            )
        else:
            # Block other requests (images, CSS, JS)
            request.abort()
    
    driver.request_interceptor = interceptor
    return driver

@pytest.fixture
def scraper(mock_driver):
    scraper = BooksScraper()
    scraper.driver = mock_driver
    return scraper

def test_scraper(scraper):
    html = scraper.download(URL)
    links = scraper.parse(html)
    assert links == LINKS["url"].to_list()
    df = scraper.transform(links)
    assert df.equals(LINKS)
```

### Performance Comparison

| Strategy | Execution Time | Test Coverage |
|----------|---------------|---------------|
| Mocking | ~0.01s | parse(), transform() only |
| Patching | ~0.01s | parse(), transform() only |
| Interception | ~0.76s | All methods including download() |

## Test Pyramid

Structure your test suite following the test pyramid:

```
                    ┌─────────────────┐
                    │  End-to-End     │  Few, Slow, High-Level
                    │  Tests (5-10%)  │
                    ├─────────────────┤
                    │  Integration    │  Some, Medium Speed
                    │  Tests (15-25%) │
                    ├─────────────────┤
                    │    Unit Tests   │  Many, Fast, Isolated
                    │  (70-80%)       │
                    └─────────────────┘
```

### Separating Test Types

```
tests/
├── __init__.py
├── unit/
│   ├── test_calculator.py
│   └── test_user.py
└── integration/
    └── test_api.py
```

```python
# tests/unit/test_calculator.py
def test_add_two_numbers():
    from calculator import add
    assert add(2, 3) == 5

# tests/integration/test_user_service.py
def test_create_user_with_database(db_connection):
    from services import UserService
    service = UserService(db_connection)
    user = service.create_user("alice@test.com", "password123")
    # Verify database state
    assert db_connection.query("SELECT * FROM users WHERE id = ?", user.id)
```

## Markers for Test Organization

Use markers to categorize and selectively run tests:

```python
import pytest

@pytest.mark.slow
def test_large_dataset_processing():
    # This test takes several seconds
    process_millions_of_records()

@pytest.mark.integration
@pytest.mark.requires_database
def test_database_transaction():
    # Integration test requiring database
    perform_database_operations()
```

```bash
# Run only fast tests
pytest -m "not slow"

# Run integration tests
pytest -m integration

# Run tests matching multiple markers
pytest -m "integration and requires_database"
```

```ini
# pytest.ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    requires_database: marks tests requiring database access
```

## Testing Asynchronous Code

Modern Python applications often use async/await:

```python
import pytest
import asyncio

async def fetch_data_async(url):
    """Async function to fetch data."""
    await asyncio.sleep(0.1)  # Simulate network delay
    return {"status": "success", "data": [1, 2, 3]}

@pytest.mark.asyncio
async def test_fetch_data_async():
    result = await fetch_data_async("https://api.example.com/data")
    assert result["status"] == "success"
    assert len(result["data"]) == 3
```

Install required packages:
```bash
pip install pytest-asyncio
```

## Property-Based Testing with Hypothesis

Instead of testing specific examples, generate random test cases:

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=1000))
def test_factorial_always_positive(n):
    from math_utils import factorial
    result = factorial(n)
    assert result > 0  # Factorial always positive for n ≥ 0

@given(st.text(min_size=1, max_size=100))
def test_string_reversal(text):
    # Test that reversing twice returns original
    assert text[::-1][::-1] == text
```

Hypothesis generates hundreds of test cases automatically, finding edge cases you wouldn't think to test.

```bash
pip install hypothesis
```

## Common Pitfalls and Solutions

### Flaky Tests

**Problem**: Tests that intermittently pass or fail without code changes.

**Causes**:
- Race conditions in async code
- Time-dependent logic
- Shared state between tests
- External service dependencies

**Solutions**:
```python
# BAD: Time-dependent test
import time

def test_cache_expiration():
    cache.set("key", "value", ttl=1)
    time.sleep(1.1)  # Flaky on slow systems
    assert cache.get("key") is None

# GOOD: Mock time
from unittest.mock import patch
import datetime

def test_cache_expiration_with_mock():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime.datetime(2024, 1, 1, 12, 0)
        cache.set("key", "value", ttl=60)
        
        # Advance time
        mock_datetime.now.return_value = datetime.datetime(2024, 1, 1, 12, 1, 1)
        assert cache.get("key") is None
```

### Over-Mocking

**Problem**: Mocking so extensively that tests don't validate real behavior.

```python
# BAD: Over-mocked test
@patch('database.connect')
@patch('database.query')
@patch('database.commit')
@patch('database.close')
def test_user_creation(mock_close, mock_commit, mock_query, mock_connect):
    # This test validates mock interactions, not real logic
    mock_query.return_value = True
    create_user("alice")
    assert mock_commit.called

# GOOD: Use real database with test fixtures
@pytest.fixture
def test_db():
    db = Database(":memory:")  # Use in-memory SQLite
    db.create_schema()
    yield db
    db.close()

def test_user_creation(test_db):
    user = create_user("alice", db=test_db)
    assert test_db.get_user(user.id)["name"] == "alice"
```

### Slow Test Suites

**Problem**: Test suite takes too long to run, discouraging frequent testing.

**Solutions**:
1. **Use pytest-xdist for parallel execution**:
```bash
pip install pytest-xdist
pytest -n auto  # Auto-detect CPU cores
```

2. **Optimize fixtures with appropriate scopes**:
```python
@pytest.fixture(scope="session")  # Create once, not per test
def expensive_resource():
    return load_large_dataset()
```

3. **Use markers to skip slow tests during development**:
```bash
pytest -m "not slow"  # Skip tests marked as slow
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest
        entry: pytest tests/unit/
        language: system
        pass_filenames: false
        always_run: true
```

## Test Coverage Best Practices

### Measuring Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Coverage Guidelines

- **Aim for 80%+ coverage**, but don't obsess over 100%
- **Focus on critical paths**: authentication, payment processing, data validation
- **Don't test framework code**: Django models, Flask routes
- **Exclude non-critical code**: `__repr__` methods, simple getters/setters

```ini
# pytest.ini
[pytest]
addopts = --cov=src --cov-report=term-missing --cov-fail-under=80
```

```ini
# .coveragerc
[run]
omit = */tests/* */migrations/* */venv/* */setup.py
```

## Test-Driven Development (TDD) Cycle

1. **Write a failing test** for new functionality
2. **Write minimal code** to make the test pass
3. **Refactor** while keeping tests green
4. **Repeat**

```python
# Step 1: Write failing test
def test_user_password_hashing():
    user = User("alice@test.com", "password123")
    # This will fail - hash_password() doesn't exist yet
    assert user.password != "password123"
    assert user.verify_password("password123") is True

# Step 2: Implement minimal code
import hashlib

class User:
    def __init__(self, email, password):
        self.email = email
        self.password = self.hash_password(password)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        return self.password == self.hash_password(password)

# Step 3: Test passes, refactor for security (use bcrypt, add salt, etc.)
```

## Troubleshooting

### Test Discovery Issues

**Problem**: pytest doesn't find your tests.

**Solution**: Ensure naming conventions:
```bash
# Debug test discovery
pytest --collect-only -v
```

### Import Errors in Tests

**Problem**: `ModuleNotFoundError` when running tests.

**Solution**: Ensure proper project structure and use `src/` layout:
```bash
# Install package in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Fixture Dependency Issues

**Problem**: Fixtures not executing in correct order.

**Solution**: Use explicit fixture dependencies:
```python
@pytest.fixture
def database():
    db = Database()
    db.create_tables()
    return db

@pytest.fixture
def user_data(database):  # Explicitly depends on database
    return database.insert_user("test@example.com")
```

## Recommended pytest Plugins

| Plugin | Purpose |
|--------|---------|
| pytest-cov | Coverage reporting |
| pytest-mock | Mocking utilities |
| pytest-asyncio | Async testing support |
| pytest-xdist | Parallel test execution |
| pytest-timeout | Test timeout enforcement |
| pytest-randomly | Random test ordering |
| pytest-cases | Parametrized test cases |
| hypothesis | Property-based testing |

```bash
pip install pytest-cov pytest-mock pytest-asyncio pytest-xdist pytest-timeout pytest-randomly hypothesis
```

## Summary

Effective testing is a skill that separates good developers from great ones. Key takeaways:

1. **Follow the AAA pattern** for clear, maintainable tests
2. **Maintain test isolation** to prevent flaky tests
3. **Use fixtures** for reusable test setup
4. **Parametrize tests** to cover multiple scenarios efficiently
5. **Mock external dependencies** appropriately
6. **Structure tests with the pyramid** in mind
7. **Invest in CI/CD** for automated testing
8. **Aim for meaningful coverage**, not 100%

Testing best practices continue to evolve. Stay current with pytest updates and emerging patterns to keep your test suite valuable rather than a maintenance burden.
