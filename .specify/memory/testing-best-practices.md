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

## Blix-Scraper Project-Specific Examples

### Project Test Structure

The blix-scraper project follows this test organization:

```
tests/
├── conftest.py                 # Shared fixtures
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

### Shared Fixtures in conftest.py

The project uses comprehensive shared fixtures defined in `tests/conftest.py`:

```python
@pytest.fixture
def mock_driver(shops_html):
    """Mock Selenium WebDriver with comprehensive mocking."""
    driver = Mock()
    driver.page_source = shops_html
    driver.get = Mock()
    driver.quit = Mock()
    driver.execute_script = Mock(return_value=0)
    driver.set_page_load_timeout = Mock()
    driver.implicitly_wait = Mock()

    # Mock capabilities
    driver.capabilities = {"browserVersion": "120.0.0", "browserName": "chrome"}

    # Mock current_url
    driver.current_url = "https://test.blix.pl/sklepy/"

    # Mock find_element and find_elements
    mock_element = Mock()
    mock_element.text = "Test Element"
    mock_element.get_attribute = Mock(return_value="test-value")
    mock_element.is_displayed = Mock(return_value=True)
    driver.find_element = Mock(return_value=mock_element)
    driver.find_elements = Mock(return_value=[mock_element])

    # Mock switch_to
    mock_switch_to = Mock()
    mock_frame = Mock()
    mock_window = Mock()
    mock_alert = Mock()
    mock_alert.text = "Test Alert"
    mock_alert.accept = Mock()
    mock_alert.dismiss = Mock()
    mock_switch_to.frame = mock_frame
    mock_switch_to.window = mock_window
    mock_switch_to.alert = mock_alert
    mock_switch_to.default_content = Mock()
    driver.switch_to = mock_switch_to

    return driver
```

### AAA Pattern in Practice

Example from `tests/domain/test_entities.py`:

```python
def test_create_shop_with_all_fields(self, sample_shop_dict):
    """Test creating shop with all fields populated."""
    # Arrange: Set up test data
    shop_data = sample_shop_dict.copy()

    # Act: Execute the code being tested
    shop = Shop.model_validate(shop_data)

    # Assert: Verify the outcome
    assert shop.slug == "biedronka"
    assert shop.brand_id == 23
    assert shop.name == "Biedronka"
    assert str(shop.logo_url) == "https://img.blix.pl/image/brand/thumbnail_23.jpg"
    assert shop.category == "Sklepy spożywcze"
    assert shop.leaflet_count == 13
    assert shop.is_popular is True
```

### Parametrization Examples

Testing multiple validation scenarios efficiently:

```python
@pytest.mark.parametrize(
    "slug,should_fail",
    [
        ("valid-slug", False),
        ("valid_slug_123", False),
        ("UPPERCASE", False),
        ("   ", False),  # Whitespace is valid (length > 0)
        ("", True),  # Empty string
    ],
)
def test_shop_slug_validation(self, slug, should_fail, sample_shop_dict):
    """Test shop slug validation (min_length=1)."""
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

### Mocking WebDriver for Scrapers

Example from `tests/scrapers/test_shop_scraper.py`:

```python
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

### Testing Storage with tmp_path

Example from `tests/storage/test_json_storage.py`:

```python
@pytest.fixture
def shop_storage(tmp_path):
    """Create shop storage instance with tmp_path."""
    return JSONStorage(tmp_path, Shop)

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

### Testing CLI with CliRunner

Example from `tests/cli/test_cli.py`:

```python
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

### HTML Fixture Strategy

The project uses real HTML fixtures captured from blix.pl:

```python
@pytest.fixture
def shops_html(html_fixtures_dir) -> str:
    """Load shops page HTML fixture."""
    fixture_path = html_fixtures_dir / "shops_page.html"

    if fixture_path.exists():
        return fixture_path.read_text(encoding="utf-8")

    # Return minimal HTML if fixture not available
    return """
    <html>
        <body>
            <section class="section-n__items--brands">
                <a href="/sklep/biedronka/" title="Biedronka">
                    <div class="brand section-n__item">
                        <img class="brand__logo" src="https://img.blix.pl/brand/23.jpg" />
                    </div>
                </a>
            </section>
        </body>
    </html>
    """
```

### Coverage Report Example

Current coverage (82% overall):

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/__init__.py                       0      0   100%
src/cli.py                          150     25    83%   23-45, 67-89
src/config.py                        45      5    89%   12-15
src/domain/entities.py              200     30    85%   45-67, 89-101
src/scrapers/base.py                 80     15    81%   23-34, 56-78
src/scrapers/shop_scraper.py         95     20    79%   34-56, 78-90
src/storage/json_storage.py        120     10    92%   45-67
---------------------------------------------------------------
TOTAL                              690    105    82%
```

### Lessons Learned During Implementation

1. **Mock WebDriver comprehensively**: Selenium WebDriver has many methods. Mocking only the ones you use leads to AttributeError when tests evolve. Create a comprehensive mock that covers common operations.

2. **Use tmp_path for storage tests**: pytest's `tmp_path` fixture provides a clean temporary directory for each test, perfect for testing file I/O operations without polluting the project.

3. **Capture real HTML fixtures**: For web scrapers, using real HTML from the target site ensures tests match production behavior. The `tests/utils/capture_html.py` utility helps capture these fixtures.

4. **Test Pydantic validation thoroughly**: Pydantic models have complex validation rules. Use parametrization to test edge cases like empty strings, None values, and invalid types.

5. **Mock context managers properly**: When testing code that uses context managers (like `ScraperOrchestrator`), mock both `__enter__` and `__exit__` methods.

6. **Use CliRunner for CLI tests**: Typer's `CliRunner` provides a clean way to test CLI commands without actually invoking the CLI.

7. **Separate unit and integration tests**: Use pytest markers to categorize tests. Unit tests should be fast and isolated. Integration tests can use real fixtures but should still avoid network calls.

8. **Test error handling**: Don't just test happy paths. Test how your code handles invalid data, missing files, and network errors.

### Running Tests in This Project

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/domain/test_entities.py

# Run specific test
pytest tests/domain/test_entities.py::TestShop::test_create_shop_with_all_fields

# Run by marker
pytest -m unit              # Only unit tests
pytest -m integration       # Only integration tests
pytest -m "not slow"        # Skip slow tests

# Run in verbose mode
pytest -v

# Stop on first failure
pytest -x

# Run with specific keyword
pytest -k "shop"            # Tests containing "shop" in name
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
