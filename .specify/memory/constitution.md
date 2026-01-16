<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0 (MINOR - new principles added)
- Added sections: VI, VII, VIII, IX, X, XI (6 new principles)
- Removed sections: None
- Templates requiring updates: ✅ (no existing templates to update)
- Follow-up TODOs: None
-->

# blix-scraper Constitution

## Core Principles

### I. uv-First Dependency Management
All dependencies MUST be managed exclusively via `uv` for reproducible, fast package management. Dependencies are defined in `pyproject.toml` with version constraints. No manual `pip` invocations in CI/CD or development workflows. Virtual environments are created and activated automatically by uv. Lock files (`uv.lock`) MUST be committed to ensure deterministic builds across all environments.

### II. Test-Driven Development
All new features MUST have corresponding tests written before implementation. Tests MUST use pytest framework following the AAA pattern (Arrange-Act-Assert). Unit tests MUST achieve minimum 70% coverage. Tests MUST be isolated and not depend on execution order or external services. Mock all external dependencies (network, filesystem, time) to ensure fast, reliable test execution.

### III. Type Safety
All Python code SHOULD use type hints for function signatures, class attributes, and public APIs. Runtime type validation SHOULD be implemented using Pydantic for data models. Type checking SHOULD pass `mypy` with strict mode enabled. This ensures code clarity, enables better IDE support, and catches errors early.

### IV. CLI-First Design
All functionality MUST be accessible via command-line interface using Typer. Commands MUST follow consistent patterns: `<verb> <noun>` structure. Output SHOULD support both human-readable and JSON formats via `--json` flag. Error messages MUST be clear, actionable, and exit with appropriate status codes.

### V. Web Scraping Best Practices
Scrapers MUST respect `robots.txt` when available. User-Agent header MUST identify the scraper. Rate limiting MUST be implemented to avoid overloading targets. HTML parsing SHOULD use BeautifulSoup4 with lxml parser for performance. All HTTP requests SHOULD have appropriate timeouts.

### VI. Browser Automation Patterns
Browser automation MUST use `undetected-chromedriver` for evading detection when required. Headless mode SHOULD be used in CI/CD environments for performance. Browser instances MUST be properly closed in finally blocks or using context managers. Profile management SHOULD be configured for consistent behavior across runs. Anti-detection measures SHOULD be kept up to date.

### VII. Input Sanitization
All user inputs MUST be validated before processing. External data MUST be sanitized to prevent injection attacks. File paths MUST be validated to prevent path traversal vulnerabilities. URL inputs MUST be validated against allowlist of permitted domains. User-provided data MUST be escaped when displayed or logged.

### VIII. Data Storage Patterns
Data storage MUST use JSON format for persistence. Storage operations MUST validate data against Pydantic models before writing. File writes MUST use atomic operations (write to temp, then rename). Backup copies SHOULD be created before overwriting existing data. Storage directory MUST be configurable via environment variable or CLI argument.

### IX. Structured Logging
All applications MUST use structured logging with consistent format. Log levels MUST be used appropriately: DEBUG for detailed info, INFO for operations, WARNING for issues, ERROR for failures. Log messages MUST include context (request ID, operation type). Error logging MUST include stack traces for debugging. Logs SHOULD be output to stdout in JSON format for container environments.

### X. Error Handling
All network operations MUST implement retry logic with exponential backoff. Transient failures SHOULD be retried automatically (3 attempts default). User-facing error messages MUST be user-friendly, avoiding technical jargon. Errors MUST be logged with sufficient context for debugging. The application MUST exit gracefully with appropriate exit codes.

### XI. Documentation Standards
All public functions and classes MUST have docstrings following Google style. Module-level documentation MUST explain purpose and usage. README.md MUST be updated when new features are added. API documentation MUST be generated for CLI commands. Breaking changes MUST be documented in changelog.

## Development Workflow

### Code Review Requirements
- All changes MUST go through pull request before merging to main
- PRs MUST have at least one approval
- Tests MUST pass before merge
- Coverage MUST not decrease by more than 5% without justification
- Linting (Ruff) and type checking (mypy) MUST pass

### Quality Gates
- Unit tests: 70% minimum coverage
- Integration tests: Required for CLI commands and storage layer
- All tests MUST pass in CI before merge
- No warnings allowed in pytest runs

### Version Control
- Main branch is protected
- Feature branches created from main
- Commit messages follow Conventional Commits format
- Releases tagged with semantic versioning

## Governance

### Amendment Procedure
Constitution amendments require:
1. Documentation of proposed change
2. Team approval
3. Migration plan if applicable
4. Version bump according to semantic versioning rules

### Compliance Review
All PRs MUST verify:
- Dependencies managed via uv
- Tests written for new functionality
- Type hints present
- CLI interface follows patterns
- Scraping practices respect target sites
- Docstrings added for new functions
- Logging implemented for operations

### Versioning Policy
- MAJOR: Backward incompatible changes to principles or workflow
- MINOR: New principles or expanded guidance
- PATCH: Clarifications, wording fixes

**Version**: 1.1.0 | **Ratified**: 2026-01-16 | **Last Amended**: 2026-01-16
