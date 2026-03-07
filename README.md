# Blix Scraper

![Tests](https://github.com/seszele64/blix-scraper/workflows/Tests/badge.svg)

Web scraper for [blix.pl](https://blix.pl) promotional leaflets. Extracts shop information, leaflets, product offers, and keywords.

## Features

- 🏪 **Shop Scraping**: Extract all retail brands from blix.pl
- 📰 **Leaflet Extraction**: Get promotional flyers with validity dates
- 🛒 **Offer Scraping**: Extract product offers with prices and positions
- 🏷️ **Keyword Tagging**: Capture product categories and keywords
- 🤖 **Anti-Detection**: Uses undetected-chromedriver
- 📊 **CLI Interface**: Easy-to-use command-line tools
- 🔍 **Search**: Search products across multiple shops

## Installation

### Requirements

- Python 3.11+
- Google Chrome browser
- Linux/macOS/Windows

### Setup

```bash
# Clone repository
git clone https://github.com/seszele64/blix-scraper
cd blix-scraper

# Install dependencies using uv (recommended - faster and better caching)
uv sync

# Alternative using pip
pip install -r requirements.txt
```

### Configuration

Create `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` to configure:
```env
HEADLESS=false          # Run Chrome in headless mode
LOG_LEVEL=INFO         # Logging level
REQUEST_DELAY_MIN=2.0  # Min delay between requests (seconds)
REQUEST_DELAY_MAX=5.0  # Max delay between requests (seconds)
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [docs/_index.md](docs/_index.md) | Documentation navigation index |
| [docs/user-guide.md](docs/user-guide.md) | Complete user guide with installation and usage |
| [docs/developer-guide.md](docs/developer-guide.md) | Developer guide for contributing |
| [docs/api-reference.md](docs/api-reference.md) | Complete API reference |
| [docs/architecture.md](docs/architecture.md) | System architecture documentation |
| [docs/domain-model.md](docs/domain-model.md) | Domain model documentation |

### Quick Links

- **New to blix-scraper?** Start with the [User Guide](docs/user-guide.md)
- **Want to contribute?** See the [Developer Guide](docs/developer-guide.md)
- **Need API details?** Check the [API Reference](docs/api-reference.md)
- **Looking for examples?** See the [Examples README](examples/README.md)

## Examples

Practical example scripts are available in the `examples/` directory:

| Script | Description | Difficulty |
|--------|-------------|------------|
| [01_scrape_single_shop.py](examples/01_scrape_single_shop.py) | Scrape all data for a single shop | Beginner |
| [02_scrape_multiple_shops.py](examples/02_scrape_multiple_shops.py) | Scrape multiple shops with error handling | Beginner |
| [03_analyze_data.py](examples/03_analyze_data.py) | Analyze scraped data and find deals | Intermediate |
| [04_search_offers.py](examples/04_search_offers.py) | Interactive product search | Intermediate |
| [05_export_csv.py](examples/05_export_csv.py) | Export data to CSV format | Intermediate |
| [06_scheduled_scraping.py](examples/06_scheduled_scraping.py) | Periodic scraping with change detection | Advanced |
| [07_search_products.py](examples/07_search_products.py) | Search and analyze products | Advanced |
| [08_debug_search.py](examples/08_debug_search.py) | Debug search page structure | Advanced |

See [examples/README.md](examples/README.md) for detailed example documentation.

## Usage

### CLI Commands

**Scrape all shops:**
```bash
uv run python -m src.cli scrape-shops
```

**Scrape leaflets for a shop:**
```bash
uv run python -m src.cli scrape-leaflets biedronka
```

**Scrape offers for a specific leaflet:**
```bash
uv run python -m src.cli scrape-offers biedronka 457727
```

**Scrape all data for a shop (leaflets + offers + keywords):**
```bash
uv run python -m src.cli scrape-full-shop biedronka
```

**List scraped shops:**
```bash
uv run python -m src.cli list-shops
```

**List available fields for an entity type:**
```bash
uv run python -m src.cli fields-list shop
uv run python -m src.cli fields-list offer
uv run python -m src.cli fields-list leaflet
```

**List leaflets for a shop (with date filtering):**
```bash
uv run python -m src.cli list-leaflets biedronka --active-only
uv run python -m src.cli list-leaflets biedronka --active-on "2026-02-27"
uv run python -m src.cli list-leaflets biedronka --valid-from "next week"
uv run python -m src.cli list-leaflets biedronka --within-range "2026-02-01 to 2026-02-28"
```

**View configuration:**
```bash
uv run python -m src.cli config
```

### Options

- `--headless`: Run browser in headless mode (faster, no UI)
- `--active-only`: Only process active leaflets
- `--active-on DATE`: Filter leaflets active on a specific date
- `--valid-from DATE`: Filter leaflets valid from a date
- `--within-range RANGE`: Filter leaflets within a date range (e.g., "2026-02-01 to 2026-02-28")
- `--save` / `-s`: Save results to JSON file
- `--output` / `-o`: Custom output directory (default: `./data/`)
- `--dated-dirs`: Save to year/month/day subdirectories
- `--fields`: Include only specific fields (comma-separated)
- `--exclude`: Exclude specific fields (comma-separated)

### JSON Export

Save scraped data to JSON files with optional field filtering:

```bash
# Save all data to JSON
uv run python -m src.cli scrape-shops --save

# Save to custom output path
uv run python -m src.cli scrape-shops --save --output ./my-data/shops.json

# Save with dated directory structure
uv run python -m src.cli scrape-shops --save --dated-dirs

# Include only specific fields
uv run python -m src.cli scrape-shops --fields name,slug --save

# Exclude specific fields
uv run python -m src.cli scrape-offers biedronka 457727 --exclude image_url --save
```

### Field Filtering

Control which fields are included in JSON exports:

```bash
# List available fields for an entity
uv run python -m src.cli fields-list shop
uv run python -m src.cli fields-list leaflet
uv run python -m src.cli fields-list offer
uv run python -m src.cli fields-list search_result

# Include only specific fields (comma-separated)
uv run python -m src.cli scrape-shops --fields name,slug --save
uv run python -m src.cli scrape-leaflets biedronka --fields name,valid_from,valid_until --save
uv run python -m src.cli scrape-offers biedronka 457727 --fields name,price --save

# Exclude specific fields (useful for removing large image URLs)
uv run python -m src.cli scrape-shops --exclude logo_url --save
uv run python -m src.cli scrape-offers biedronka 457727 --exclude image_url --save
```

**Note**: `--fields` and `--exclude` can be used together. When both are specified,
`--fields` is applied first (to include only those fields), then `--exclude` is applied
to remove any unwanted fields from that set.

Example:
```bash
# Include only name and price fields, then exclude price
blix-scraper scrape-shops --fields name,price --exclude price --save
```

### Date Filtering

Filter leaflets and offers by date ranges:

```bash
# Show leaflets active on a specific date
uv run python -m src.cli list-leaflets biedronka --active-on "2026-02-27"

# Show leaflets valid from a date
uv run python -m src.cli list-leaflets biedronka --valid-from "next week"

# Show leaflets within a date range
uv run python -m src.cli list-leaflets biedronka --within-range "2026-02-01 to 2026-02-28"

# Search with date filter
uv run python -m src.cli search "milk" --active-on "today"
uv run python -m src.cli search "coffee" --valid-from "next Monday"
```

Supported date formats:
- ISO dates: `2026-02-27`, `2026-02-27 14:30`
- Natural language: `today`, `tomorrow`, `yesterday`
- Relative dates: `next week`, `next weekend`, `end of month`

### Examples

```bash
# Scrape Biedronka leaflets in headless mode
uv run python -m src.cli scrape-leaflets biedronka --headless

# Scrape all data for Lidl (active leaflets only)
uv run python -m src.cli scrape-full-shop lidl --active-only --headless

# Show all shops with their leaflet counts
uv run python -m src.cli list-shops

# Search for products across all shops
uv run python -m src.cli search "kawa"

# Export shops to JSON with only name and slug
uv run python -m src.cli scrape-shops --fields name,slug --save

# Export offers without large image URLs
uv run python -m src.cli scrape-offers biedronka 457727 --exclude image_url --save

# Save data in dated subdirectories (e.g., data/2026/03/07/)
uv run python -m src.cli scrape-full-shop biedronka --save --dated-dirs

# Combine field filtering with dated directories
uv run python -m src.cli scrape-leaflets biedronka --fields name,valid_from,valid_until --save --dated-dirs
```

## Testing

### Run Tests

```bash
# All tests (using uv - recommended)
uv run pytest

# With coverage
uv run pytest --cov=src tests/

# Specific test file
uv run pytest tests/domain/test_entities.py

# Verbose output
uv run pytest -v
```

### CI/CD Pipeline

This project uses GitHub Actions for continuous integration and automated testing.

#### Workflow Features

- **Triggers**: Runs on push and pull requests to `main` and `develop` branches
- **Multi-OS Testing**: Tests on Ubuntu, Windows, and macOS
- **Python Version**: Python 3.11
- **Dependency Management**: Uses Poetry for reproducible builds
- **Coverage Gate**: Requires minimum 70% code coverage
- **Codecov Integration**: Uploads coverage reports for tracking

#### Coverage Requirements

The CI pipeline enforces a **70% minimum code coverage** requirement. Pull requests that fall below this threshold will fail the CI checks and cannot be merged.

View the workflow configuration in [`.github/workflows/test.yml`](.github/workflows/test.yml).

#### Required Secrets

For private repositories, add the following secret to your GitHub repository settings:

- **`CODECOV_TOKEN`**: Required for Codecov integration
  - Get your token from [codecov.io](https://codecov.io)
  - Navigate to: Repository Settings → Secrets and variables → Actions → New repository secret

For public repositories, Codecov works without a token.

### Branch Protection Rules

To maintain code quality and ensure all changes are properly tested, configure branch protection rules for the `main` branch.

#### Recommended Settings

**GitHub UI Configuration:**

1. Navigate to: Repository Settings → Branches
2. Click "Add rule" for `main` branch
3. Configure the following settings:

##### Required Checks

Enable these required status checks:
- ✅ `Test on ubuntu-latest with Python 3.11`
- ✅ `Test on windows-latest with Python 3.11`
- ✅ `Test on macos-latest with Python 3.11`

##### Protection Rules

- **Require a pull request before merging**: ✅ Enabled
  - Require approvals: 1 (or more for your team)
  - Dismiss stale PR approvals when new commits are pushed: ✅ Enabled
  - Require review from Code Owners: ✅ Recommended

- **Require status checks to pass before merging**: ✅ Enabled
  - Require branches to be up to date before merging: ✅ Enabled

- **Do not allow bypassing the above settings**: ✅ Enabled (for admins)

- **Require branches to be up to date before merging**: ✅ Enabled

- **Require linear history**: ✅ Recommended (prevents merge commits)

##### Optional Rules

- **Restrict who can push to matching branches**: Add only maintainers
- **Allow force pushes**: ❌ Disabled
- **Allow deletions**: ❌ Disabled

#### Workflow

1. Create a feature branch from `develop` or `main`
2. Make changes and commit with clear messages
3. Push to your fork or repository
4. Create a pull request
5. CI pipeline runs automatically (tests on all OS platforms)
6. Address any failing tests or coverage issues
7. Request review from team members
8. Once approved and all checks pass, merge the PR

#### Coverage Gate Details

The CI pipeline uses `--cov-fail-under=70` to enforce coverage requirements:

- **Terminal Report**: Shows missing lines during CI run
- **XML Report**: Uploaded to Codecov for historical tracking
- **Failure**: Build fails if coverage drops below 70%
- **Fix**: Add tests for uncovered code paths before merging

To check coverage locally before pushing:

```bash
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

### Capture Real HTML Fixtures

```bash
uv run python -m tests.utils.capture_html \
  --url https://blix.pl/sklepy/ \
  --output tests/fixtures/html/shops_page.html
```

## Development

**AI Agents**: See [AGENTS.md](AGENTS.md) for agent-specific instructions.

### Project Structure

```
blix-scraper/
├── src/
│   ├── cli/              # CLI interface (Typer commands)
│   ├── domain/           # Domain entities (Pydantic models)
│   ├── scrapers/         # Scraper implementations
│   ├── services/         # Service layer (ScraperService)
│   ├── webdriver/        # Selenium driver factory
│   ├── config.py         # Configuration
│   └── logging_config.py # Logging setup
├── tests/
│   ├── fixtures/         # Test HTML fixtures
│   ├── domain/          # Entity tests
│   ├── scrapers/        # Scraper tests
│   └── cli/             # CLI tests
├── docs/                # Documentation
├── examples/            # Example scripts
└── logs/                # Application logs
```

### Code Quality

This project uses Ruff for linting - an extremely fast Python linter written in Rust that replaces multiple tools (flake8, isort, pyupgrade, etc.).

```bash
# Check for linting issues (using uv - recommended)
uv run ruff check src/ tests/

# Auto-fix issues (most issues can be fixed automatically)
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/

# Type checking
uv run mypy src/
```

## Architecture

- **Domain Model**: Pydantic entities (Shop, Leaflet, Offer, Keyword)
- **Scrapers**: Template Method pattern with BeautifulSoup parsing
- **Service Layer**: ScraperService with context manager (pure data return)
- **WebDriver**: undetected-chromedriver with webdriver-manager
- **CLI**: Typer-based commands with Rich output

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Legal & Ethics

⚠️ **Important**: This scraper is for educational purposes only.

- Respects `robots.txt`
- Implements rate limiting (2-5s delays)
- Uses realistic User-Agent
- Only scrapes public promotional data
- No PII collection

**Use responsibly and check blix.pl's terms of service before scraping.**

## Troubleshooting

### Chrome Version Mismatch

If you see ChromeDriver version errors:
```bash
# webdriver-manager will auto-download correct version
# Just restart the scraper
```

### Element Not Found Errors

- Website structure may have changed
- Check HTML fixtures are up-to-date
- Inspect actual page in browser

### Slow Scraping

- Use `--headless` flag for faster execution
- Adjust delays in `.env` (minimum 2s recommended)

## License

MIT License - See LICENSE file

## Contributing

Contributions are welcome! Please read our documentation first:

1. **New contributors**: Start with the [Developer Guide](docs/developer-guide.md)
2. **Coding standards**: Follow the [coding guidelines](docs/developer-guide.md#coding-standards)
3. **Testing**: Learn about [testing requirements](docs/developer-guide.md#testing)
4. **Submit changes**: Create a pull request with tests

## Contact

For issues and questions, please open a GitHub issue.