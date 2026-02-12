# Agent Instructions for blix-scraper

AI agent guide for this Python web scraper project.

## Project Overview

- **Type**: Python web scraper for blix.pl promotional leaflets
- **Python**: 3.11+
- **Architecture**: Domain-driven design with template method pattern
- **Package Manager**: uv (preferred) or pip

## Build/Lint/Test Commands

```bash
# Install dependencies
uv sync
pip install -r requirements.txt

# Run tests
pytest                     # All tests
pytest -x                  # Stop on first failure
pytest -v                  # Verbose
pytest tests/test_file.py  # Single file
pytest -k test_name        # By name pattern
pytest::test_file.py::test_function  # Single test

# Coverage
pytest --cov=src --cov-report=term-missing

# Linting and Formatting
ruff check src/ tests/
ruff check --fix src/ tests/
black src/ tests/
black --check src/ tests/

# Type Checking
mypy src/

# Run Application
python -m src
uv run python -m src
```

## Code Style Guidelines

### Formatting & Naming
- **Line length**: 100 characters (Black config in pyproject.toml)
- **Target Python**: 3.11+
- **Classes**: PascalCase (`ShopScraper`, `Leaflet`)
- **Functions/variables**: snake_case (`download_page`)
- **Constants**: UPPER_SNAKE_CASE (`BASE_URL`)
- **Private**: Leading underscore (`_parse_html`)

### Imports
Use absolute imports within `src/`. Group: stdlib, third-party, local. Ruff handles sorting.

```python
from datetime import datetime
from bs4 import BeautifulSoup
from src.domain.entities import Shop
```

### Type Hints
- **Required**: All parameters and return types
- **Strict mode**: mypy strict enabled
- Use `| None` syntax (Python 3.11+)

```python
def fetch_data(url: str, timeout: int = 30) -> dict | None:
    ...
```

### Error Handling
Use specific exceptions, log with structlog context, use `try/except/finally` for cleanup.

```python
from structlog import get_logger

logger = get_logger(__name__)

def safe_operation():
    try:
        result = risky_call()
    except ValueError as e:
        logger.error("operation_failed", error=str(e))
        raise
    finally:
        cleanup()
```

### Domain Entities (Pydantic v2)

```python
from pydantic import BaseModel, Field
from decimal import Decimal

class Offer(BaseModel):
    id: str
    name: str
    price: Decimal = Field(decimal_places=2)
```

### Scraper Pattern

```python
from src.scrapers.base import BaseScraper

class NewScraper(BaseScraper):
    def download(self, url: str) -> str: ...
    def parse(self, html: str) -> list: ...
```

### Testing
- Use pytest fixtures in `conftest.py`
- Follow AAA pattern (Arrange-Act-Assert)
- Mock external dependencies
- Minimum 70% coverage
- Store HTML fixtures in `tests/fixtures/`

### Documentation
Google-style docstrings for all public methods.

```python
def process_data(data: dict) -> list:
    """Process raw data into structured format.
    
    Args:
        data: Raw data dictionary from scraper.
        
    Returns:
        List of processed items.
        
    Raises:
        ValueError: If data format is invalid.
    """
```

## Project Constitution

See `.specify/memory/constitution.md` for core principles:
- uv-first dependency management
- Test-driven development (70%+ coverage)
- Type safety with mypy strict
- CLI-first design with Typer
- Web scraping best practices
- Structured logging with structlog
- JSON file storage (no database)

## Key Directories

- `src/`: Source code
- `tests/`: Test suite
- `docs/`: Documentation
- `examples/`: Example scripts
- `specs/`: Feature specifications
- `memories/`: Project knowledge
- `data/`: Scraped data (gitignored)
- `logs/`: Application logs (gitignored)

## References

- [Constitution](.specify/memory/constitution.md) - Project principles
- [Developer Guide](docs/developer-guide.md) - Development docs
- [Testing Best Practices](.specify/memory/testing-best-practices.md) - Testing patterns
