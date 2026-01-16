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
6. [Contributing](#contributing)
7. [Building and Releasing](#building-and-releasing)

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

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/domain/test_entities.py

# Run specific test
pytest tests/domain/test_entities.py::test_shop_creation

# Run in verbose mode
pytest -v
```

### Test Structure

```
tests/
├── fixtures/
│   ├── html/              # Real HTML samples
│   └── json/              # Expected data samples
├── domain/
│   └── test_entities.py   # Entity tests
├── scrapers/
│   └── test_shop_scraper.py  # Scraper tests
└── storage/
    └── test_json_storage.py  # Storage tests
```

### Writing Tests

#### Unit Test

```python
# tests/domain/test_shop.py
import pytest
from src.domain.entities import Shop


def test_shop_creation():
    """Test creating a Shop instance."""
    shop = Shop(
        slug="biedronka",
        name="Biedronka",
        logo_url="https://example.com/logo.png",
        leaflet_count=10,
        is_popular=True
    )

    assert shop.slug == "biedronka"
    assert shop.name == "Biedronka"
    assert shop.leaflet_count == 10
    assert shop.is_popular is True


def test_shop_validation():
    """Test Shop validation."""
    with pytest.raises(ValidationError):
        Shop(
            slug="",  # Empty slug should fail
            name="Test",
            logo_url="https://example.com/logo.png",
            leaflet_count=0
        )
```

#### Integration Test

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


def test_extract_shops(sample_html):
    """Test extracting shops from HTML."""
    # Create mock driver
    class MockDriver:
        page_source = sample_html

    scraper = ShopScraper(MockDriver())
    soup = BeautifulSoup(sample_html, 'lxml')

    shops = scraper._extract_entities(soup, "https://blix.pl/sklepy/")

    assert len(shops) > 0
    assert any(s.slug == "biedronka" for s in shops)
```

### Test Fixtures

Create realistic test fixtures:

```bash
# Capture real HTML for testing
python -m tests.utils.capture_html \
    --url https://blix.pl/sklepy/ \
    --output tests/fixtures/html/shops_page.html
```

### Code Coverage

Aim for high test coverage:

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing

# Coverage should be above 80% for new code
```

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
