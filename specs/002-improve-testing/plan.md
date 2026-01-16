# Implementation Plan: Improve Testing Infrastructure

**Branch**: `002-improve-testing` | **Date**: 2026-01-16 | **Spec**: [Link](spec.md)  
**Input**: Feature specification from `/specs/002-improve-testing/spec.md`

## Summary

Implement comprehensive testing infrastructure for the blix-scraper project with 70% unit test coverage, CI/CD pipeline via GitHub Actions, and adherence to testing best practices documented in `docs/testing-best-practices.md`. This includes configuring pytest with coverage reporting, creating organized test suites with markers, and establishing automated quality gates.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: pytest, pytest-cov, pytest-mock, GitHub Actions  
**Storage**: N/A (test infrastructure, no data persistence)  
**Testing**: pytest with coverage, mocking, and parametrization  
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

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e . pytest pytest-cov pytest-mock
      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

### Fixture Strategy

| Scope | Fixture | Purpose |
|-------|---------|---------|
| function | temp_dir | Temporary directory for test files |
| function | sample_html | Sample HTML for parsing tests |
| module | mock_driver | Mock Selenium WebDriver |
| session | test_config | Test configuration |

## Complexity Tracking

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
| research.md | ⏳ Pending | `specs/002-improve-testing/research.md` |
| data-model.md | ⏳ Pending | `specs/002-improve-testing/data-model.md` |
| quickstart.md | ⏳ Pending | `specs/002-improve-testing/quickstart.md` |
| tasks.md | ⏳ Pending | `specs/002-improve-testing/tasks.md` |
