# Blix Scraper

Web scraper for [blix.pl](https://blix.pl) promotional leaflets. Extracts shop information, leaflets, product offers, and keywords.

## Features

- 🏪 **Shop Scraping**: Extract all retail brands from blix.pl
- 📰 **Leaflet Extraction**: Get promotional flyers with validity dates
- 🛒 **Offer Scraping**: Extract product offers with prices and positions
- 🏷️ **Keyword Tagging**: Capture product categories and keywords
- 💾 **File Storage**: Simple JSON-based storage (no database required)
- 🤖 **Anti-Detection**: Uses undetected-chromedriver
- 📊 **CLI Interface**: Easy-to-use command-line tools

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

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or use Poetry
poetry install
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
python -m src.cli scrape-shops
```

**Scrape leaflets for a shop:**
```bash
python -m src.cli scrape-leaflets biedronka
```

**Scrape offers for a specific leaflet:**
```bash
python -m src.cli scrape-offers biedronka 457727
```

**Scrape all data for a shop (leaflets + offers + keywords):**
```bash
python -m src.cli scrape-full-shop biedronka
```

**List scraped shops:**
```bash
python -m src.cli list-shops
```

**List leaflets for a shop:**
```bash
python -m src.cli list-leaflets biedronka --active-only
```

**View configuration:**
```bash
python -m src.cli config
```

### Options

- `--headless`: Run browser in headless mode (faster, no UI)
- `--active-only`: Only process active leaflets

### Examples

```bash
# Scrape Biedronka leaflets in headless mode
python -m src.cli scrape-leaflets biedronka --headless

# Scrape all data for Lidl (active leaflets only)
python -m src.cli scrape-full-shop lidl --active-only --headless

# Show all shops with their leaflet counts
python -m src.cli list-shops
```

## Data Structure

Scraped data is saved in `data/` directory:

```
data/
├── shops/
│   ├── shops.json              # All shops
│   ├── biedronka.json          # Individual shop files
│   └── lidl.json
├── leaflets/
│   ├── biedronka/
│   │   ├── 457727.json
│   │   └── 457728.json
│   └── lidl/
│       └── 123456.json
├── offers/
│   ├── 457727_offers.json      # All offers for leaflet
│   └── 457728_offers.json
└── keywords/
    └── 457727_keywords.json    # Keywords for leaflet
```

### JSON Schema Examples

**Shop (shops/biedronka.json):**
```json
{
  "slug": "biedronka",
  "name": "Biedronka",
  "logo_url": "https://img.blix.pl/image/brand/thumbnail_23.jpg",
  "leaflet_count": 13,
  "is_popular": true,
  "scraped_at": "2025-10-30T12:00:00Z"
}
```

**Leaflet (leaflets/biedronka/457727.json):**
```json
{
  "leaflet_id": 457727,
  "shop_slug": "biedronka",
  "name": "Od środy",
  "cover_image_url": "https://imgproxy.blix.pl/...",
  "url": "https://blix.pl/sklep/biedronka/gazetka/457727/",
  "valid_from": "2025-10-29T00:00:00Z",
  "valid_until": "2025-11-05T23:59:59Z",
  "status": "active"
}
```

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/domain/test_entities.py

# Verbose output
pytest -v
```

### Capture Real HTML Fixtures

```bash
python -m tests.utils.capture_html \
  --url https://blix.pl/sklepy/ \
  --output tests/fixtures/html/shops_page.html
```

## Development

### Project Structure

```
blix-scraper/
├── src/
│   ├── cli/              # CLI interface
│   ├── domain/           # Domain entities
│   ├── scrapers/         # Scraper implementations
│   ├── storage/          # JSON storage
│   ├── webdriver/        # Selenium driver factory
│   ├── config.py         # Configuration
│   ├── logging_config.py # Logging setup
│   └── orchestrator.py   # Workflow orchestration
├── tests/
│   ├── fixtures/         # Test HTML fixtures
│   ├── domain/          # Entity tests
│   ├── scrapers/        # Scraper tests
│   └── storage/         # Storage tests
├── docs/                # Documentation
├── data/                # Scraped data (gitignored)
└── logs/                # Application logs
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff src/ tests/

# Type checking
mypy src/
```

## Architecture

- **Domain Model**: Pydantic entities (Shop, Leaflet, Offer, Keyword)
- **Scrapers**: Template Method pattern with BeautifulSoup parsing
- **Storage**: Simple JSON files (no database)
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