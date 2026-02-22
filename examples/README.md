# Blix Scraper Examples

Collection of example scripts demonstrating various use cases for the blix-scraper library.

## Prerequisites

Before running the examples, make sure you have:

1. **Installed the package** (using uv - recommended):
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configured the environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Scraped some data** (for examples that analyze existing data):
   ```bash
   uv run python -m src.cli scrape-shops
   uv run python -m src.cli scrape-leaflets biedronka
   ```

## Examples Overview

| # | Script | Description | Difficulty |
|---|--------|-------------|------------|
| 01 | [`01_scrape_single_shop.py`](01_scrape_single_shop.py) | Scrape all data for a single shop | Beginner |
| 02 | [`02_scrape_multiple_shops.py`](02_scrape_multiple_shops.py) | Scrape multiple shops with error handling | Beginner |
| 03 | [`03_analyze_data.py`](03_analyze_data.py) | Analyze scraped data and find deals | Intermediate |
| 04 | [`04_search_offers.py`](04_search_offers.py) | Interactive product search | Intermediate |
| 05 | [`05_export_csv.py`](05_export_csv.py) | Export data to CSV format | Intermediate |
| 06 | [`06_scheduled_scraping.py`](06_scheduled_scraping.py) | Periodic scraping with change detection | Advanced |
| 07 | [`07_search_products.py`](07_search_products.py) | Search and analyze products | Advanced |
| 08 | [`08_debug_search.py`](08_debug_search.py) | Debug search page structure | Advanced |

## Example Details

### 1. Scrape Single Shop (`01_scrape_single_shop.py`)

Basic example demonstrating how to scrape all leaflets, offers, and keywords for a single shop.

**What it demonstrates:**
- Creating a `ScraperOrchestrator` instance
- Scraping shop leaflets
- Filtering active leaflets
- Scraping offers and keywords for each leaflet
- Error handling

**Usage:**
```bash
# Using uv (recommended)
uv run python examples/01_scrape_single_shop.py
```

**Output:**
- JSON files in `data/leaflets/biedronka/`
- JSON files in `data/offers/`
- JSON files in `data/keywords/`

---

### 2. Scrape Multiple Shops (`02_scrape_multiple_shops.py`)

Demonstrates scraping multiple shops in sequence with error handling and statistics.

**What it demonstrates:**
- Processing multiple shops
- Error handling per shop
- Collecting statistics
- Displaying summary tables

**Usage:**
```bash
# Using uv (recommended)
uv run python examples/02_scrape_multiple_shops.py
```

**Customization:**
Edit the `shops` list to change which shops to scrape:
```python
shops = ["biedronka", "lidl", "kaufland", "auchan"]
```

---

### 3. Analyze Data (`03_analyze_data.py`)

Analyzes scraped data to find cheapest offers, popular categories, and statistics.

**What it demonstrates:**
- Loading data from JSON files
- Price analysis
- Category statistics
- Data filtering and sorting

**Usage:**
```bash
# Using uv (recommended)
uv run python examples/03_analyze_data.py
```

**Requirements:**
Run scraping first:
```bash
uv run python -m src.cli scrape-full-shop biedronka
```

---

### 4. Search Offers (`04_search_offers.py`)

Interactive search across all scraped offers.

**What it demonstrates:**
- Searching across multiple shops
- Cross-shop comparison
- Price statistics
- Interactive user input

**Usage:**
```bash
# Using uv (recommended)
uv run python examples/04_search_offers.py
# Enter a product name when prompted
```

**Example searches:**
- `kawa` (coffee)
- `mleko` (milk)
- `chleb` (bread)
- `masło` (butter)

---

### 5. Export CSV (`05_export_csv.py`)

Exports scraped data to CSV format for use in Excel or Google Sheets.

**What it demonstrates:**
- Converting JSON to CSV
- Creating exports directory
- Multiple export functions

**Usage:**
```bash
# Using uv (recommended)
uv run python examples/05_export_csv.py
```

**Output:**
- `exports/shops.csv` - All shops
- `exports/biedronka_offers.csv` - All offers for Biedronka

---

### 6. Scheduled Scraping (`06_scheduled_scraping.py`)

Periodic scraping with change detection (cron-like behavior).

**What it demonstrates:**
- Periodic execution
- Change detection
- New leaflet identification
- Graceful shutdown

**Usage:**
```bash
# Using uv (recommended)
uv run python examples/06_scheduled_scraping.py
# Press Ctrl+C to stop
```

**Customization:**
Change the interval or shops:
```python
shops = ["biedronka", "lidl", "kaufland"]
interval_minutes = 60  # Check every hour
```

---

### 7. Search Products (`07_search_products.py`)

Advanced search with detailed analysis and FieldFilter usage.

**What it demonstrates:**
- Using `search_products()` method
- Field filtering for selective data
- Detailed result analysis
- Brand and shop comparisons

**Usage:**
```bash
# Using uv (recommended)
uv run python examples/07_search_products.py
```

**FieldFilter Options:**
The example demonstrates different FieldFilter configurations:
- `filter_base` - Basic fields with dates
- `filter_minimal` - Only essential fields
- `filter_custom` - Custom field selection
- `filter_extended` - Extended fields

---

### 8. Debug Search (`08_debug_search.py`)

Debug script for inspecting search page structure.

**What it demonstrates:**
- Page structure analysis
- Script tag inspection
- JSON data finding
- Manual browser inspection

**Usage:**
```bash
# Using uv (recommended)
uv run python examples/08_debug_search.py kawa
```

**Note:**
This script opens a visible browser window for manual inspection. Press Enter to close.

---

## Data Location

Examples expect data in the following structure:

```
data/
├── shops/
│   ├── shops.json
│   └── {slug}.json
├── leaflets/
│   └── {shop_slug}/
│       └── {leaflet_id}.json
├── offers/
│   └── {leaflet_id}_offers.json
└── keywords/
    └── {leaflet_id}_keywords.json
```

## Customization

All examples can be customized:

1. **Change shop names**: Edit the `shops` or `shop_slug` variables
2. **Adjust intervals**: Change `interval_minutes` in scheduled scraping
3. **Modify search criteria**: Update query strings in search examples
4. **Add error handling**: Wrap operations in try/except blocks
5. **Integrate with databases**: Replace JSON storage with database calls

## Troubleshooting

### Import Errors

If you see import errors:
```bash
# Make sure you're in the project root
cd /path/to/blix-scraper

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -r requirements.txt

# Run examples from root (using uv - recommended)
uv run python examples/01_scrape_single_shop.py
```

### No Data Found

For examples that analyze existing data:
```bash
# First scrape some data
uv run python -m src.cli scrape-shops
uv run python -m src.cli scrape-leaflets biedronka
```

### Browser Issues

If you see Chrome/WebDriver errors:
```bash
# Check Chrome is installed
google-chrome --version

# Or use headless mode in examples
# (examples already use headless=True by default)
```

## Best Practices

1. **Start with simple examples** - Begin with 01 and 02
2. **Understand the API** - Read the [API Reference](../docs/api-reference.md)
3. **Handle errors** - Always use try/except blocks
4. **Use progress bars** - Rich provides good progress indicators
5. **Log appropriately** - Use the logging module for debugging
6. **Respect the website** - Use delays and don't overload the server

## Additional Resources

- [User Guide](../docs/user-guide.md) - Getting started guide
- [Developer Guide](../docs/developer-guide.md) - Contributing guidelines
- [API Reference](../docs/api-reference.md) - Complete API documentation
- [Architecture](../docs/architecture.md) - System architecture
