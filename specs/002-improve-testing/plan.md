# Implementation Plan: Improve Testing Infrastructure

**Branch**: `002-improve-testing` | **Date**: 2026-01-16 | **Spec**: [Link](spec.md)  
**Input**: Feature specification from `/specs/002-improve-testing/spec.md`

## Summary

Implement comprehensive testing infrastructure for the blix-scraper project with 70% unit test coverage, CI/CD pipeline via GitHub Actions, and adherence to testing best practices documented in `docs/testing-best-practices.md`. This includes configuring pytest with coverage reporting, creating organized test suites with markers, and establishing automated quality gates.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: pytest, pytest-cov, pytest-mock, pytest-xdist, codecov-action  
**Storage**: N/A (test infrastructure, no data persistence)  
**Testing**: pytest with coverage, mocking, parametrization, and parallel execution  
**Target Platform**: Linux server (CI/CD) and local development  
**Project Type**: Single project (CLI tool)  
**Performance Goals**: Test suite execution under 15 minutes  
**Constraints**: Coverage threshold of 70% for unit tests, CI must complete fast  
**Scale/Scope**: Existing codebase (~1000 LOC), 5 user stories, 10 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Code Quality | ✅ PASS | Testing infrastructure improves code quality |
| Testing | ✅ PASS | Core requirement of this feature |
| Documentation | ✅ PASS | Will update docs/testing-best-practices.md |

## Project Structure

### Documentation (this feature)

```text
specs/002-improve-testing/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (testing best practices research)
├── data-model.md        # Phase 1 output (test entities and fixtures)
├── quickstart.md        # Phase 1 output (running tests guide)
├── contracts/           # Phase 1 output (test contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── __main__.py
├── config.py
├── logging_config.py
├── orchestrator.py
├── cli/
│   ├── __init__.py
│   └── __main__.py
├── domain/
│   ├── __init__.py
│   └── entities.py
├── scrapers/
│   ├── __init__.py
│   ├── base.py
│   ├── keyword_scraper.py
│   ├── leaflet_scraper.py
│   ├── offer_scraper.py
│   ├── search_scraper.py
│   └── shop_scraper.py
├── storage/
│   ├── __init__.py
│   ├── field_filter.py
│   └── json_storage.py
└── webdriver/
    ├── __init__.py
    ├── driver_factory.py
    └── helpers.py

tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── test_entities.py
│   ├── test_json_storage.py
│   └── test_field_filter.py
├── integration/
│   └── __init__.py
└── scrapers/
    ├── __init__.py
    └── test_shop_scraper.py

.github/
└── workflows/
    └── test.yml         # GitHub Actions CI workflow

pytest.ini               # pytest configuration
.pytest_cache/           # pytest cache (gitignored)
```

**Structure Decision**: Using the existing project structure with enhanced test organization. Adding GitHub Actions workflow at `.github/workflows/test.yml`. Test structure follows the pyramid: unit/ for fast tests, integration/ for slower tests, and scrapers/ for domain-specific tests.

## Research & Decisions

### Testing Framework Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| pytest | De facto standard, simple assert syntax, extensive plugins | unittest (more verbose) |
| pytest-cov | Native coverage integration, supports multiple formats | coverage.py (separate tool) |
| pytest-mock | Built-in mocking, integrates with fixtures | unittest.mock (more boilerplate) |
| GitHub Actions | Already used by project, free for open source | Travis CI, CircleCI |

### Test Organization Strategy

| Test Type | Location | Purpose | Target % |
|-----------|----------|---------|----------|
| Unit Tests | tests/unit/ | Test individual functions/classes | 70-80% |
| Integration Tests | tests/integration/ | Test component interactions | 15-25% |
| Domain Tests | tests/scrapers/ | Test domain-specific behavior | 5-10% |

### CI/CD Pipeline Design

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e . pytest pytest-cov pytest-mock pytest-xdist
      
      - name: Run tests with coverage
        run: |
          pytest -n auto --cov=src --cov-report=xml --cov-report=term-missing --cov-fail-under=70
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false
```

**Pipeline Features**:
- Branch filtering (main, PRs only)
- Python 3.11 single version testing
- Pip caching for faster builds
- Parallel test execution (`-n auto`)
- Coverage fail-under threshold (70%)
- Codecov integration for coverage tracking
- 15-minute timeout for fast feedback

### Fixture Strategy

| Scope | Fixture | Purpose |
|-------|---------|---------|
| function | temp_dir | Temporary directory for test files |
| function | sample_html | Sample HTML for parsing tests |
| function | mock_driver | Mock Selenium WebDriver |
| module | test_config | Module-wide test configuration |
| session | expensive_resource | Session-wide expensive resources |

### Pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    -n auto
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=70

markers =
    unit: Tests for individual functions/classes (fast)
    integration: Tests for component interactions (medium)
    slow: Tests that take longer to run (mark for exclusion)
    scraping: Tests for scraper functionality

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning

[coverage:run]
source = src
omit = 
    */tests/*
    */__pycache__/*
    */__init__.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    def __str__
    raise NotImplementedError
    if __name__ == "__main__":
```

### Test Guidelines

#### AAA Pattern (Arrange-Act-Assert)

All tests should follow the AAA pattern for clarity:

```python
def test_shop_parsing():
    # Arrange: Setup test data and fixtures
    html = "<html>...shop data...</html>"
    soup = BeautifulSoup(html, 'html.parser')
    
    # Act: Execute the function under test
    shop = parse_shop(soup)
    
    # Assert: Verify the expected outcome
    assert shop.name == "Test Shop"
    assert shop.url == "https://test.shop"
```

#### Test Isolation

- Each test must be independent (no shared state)
- Tests must not depend on execution order
- Use fixtures for setup/teardown
- Mock external dependencies (network, filesystem)

#### Mocking Strategy

| Dependency Type | Mocking Approach |
|-----------------|------------------|
| WebDriver | `unittest.mock.MagicMock` |
| Network calls | `requests_mock` or `@patch` |
| Filesystem | `tmp_path` fixture |
| Time | `freezegun` or `time.monotonic.patch` |

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. This feature enhances existing infrastructure without conflicting with project principles.

## Next Steps

1. **Phase 0**: Research testing best practices and consolidate findings
2. **Phase 1**: Design test data models, create fixtures, setup CI/CD
3. **Phase 2**: Generate tasks.md for implementation
4. **Phase 3**: Execute implementation

## Generated Artifacts

| Artifact | Status | Path |
|----------|--------|------|
| plan.md | ✅ Complete | `specs/002-improve-testing/plan.md` |
| spec.md | ✅ Complete | `specs/002-improve-testing/spec.md` |
| research.md | ✅ Complete | `specs/002-improve-testing/research.md` |
| data-model.md | ✅ Complete | `specs/002-improve-testing/data-model.md` |
| quickstart.md | ✅ Complete | `specs/002-improve-testing/quickstart.md` |
| tasks.md | ⏳ Pending | `specs/002-improve-testing/tasks.md` |
