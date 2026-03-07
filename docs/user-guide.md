---
title: User Guide
description: Comprehensive guide for using blix-scraper
category: documentation
tags:
  - user-guide
  - getting-started
  - installation
  - usage
created: 2026-01-16
updated: 2026-01-16
---

# User Guide

Complete guide for using blix-scraper to extract promotional leaflets from blix.pl.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [CLI Commands](#cli-commands)
5. [Examples](#examples)
6. [Data Structure](#data-structure)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone and setup
git clone https://github.com/seszele64/blix-scraper
cd blix-scraper

# 2. Install with uv (recommended)
uv sync

# Or using pip:
# python -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt

# 3. Configure (optional)
cp .env.example .env

# 4. Scrape some shops
uv run python -m src.cli scrape-shops
uv run python -m src.cli scrape-leaflets biedronka

# 5. Search for products
uv run python -m src.cli search kawa
```

---

## Installation

### System Requirements

- **Python**: 3.11 or higher
- **Browser**: Google Chrome (any recent version)
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512 MB minimum (2 GB recommended)
- **Disk Space**: 100 MB for installation + data storage

### Python Environment

Create a virtual environment:

```bash
# Using venv (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Verify Python version
python --version  # Should be 3.11+
```

### Install Dependencies

**Recommended: Using uv**
```bash
# Install all dependencies (including dev)
uv sync

# Or install just production dependencies
uv sync --no-dev
```

**Alternative: Using pip**
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install individually
pip install undetected-chromedriver
pip install beautifulsoup4
pip install lxml
pip install pydantic
pip install typer
pip install rich
pip install structlog
```

### Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` to customize settings:

```env
# WebDriver settings
HEADLESS=true              # Run in headless mode (no browser UI)
LOG_LEVEL=INFO            # Logging level: DEBUG, INFO, WARNING, ERROR

# Request settings
REQUEST_DELAY_MIN=2.0     # Minimum delay between requests (seconds)
REQUEST_DELAY_MAX=5.0     # Maximum delay between requests (seconds)

# Data settings
DATA_DIR=data             # Where to save scraped data
```

---

## Basic Usage

### Using the CLI

The easiest way to use blix-scraper is through the CLI:

```bash
# View available commands
uv run python -m src.cli --help

# Scrape all shops
uv run python -m src.cli scrape-shops

# Scrape leaflets for a specific shop
uv run python -m src.cli scrape-leaflets biedronka

# Search for products
uv run python -m src.cli search kawa
```

### Using the Python API

For more control, use the Python API directly:

```python
from src.services import ScraperService

# Create service (context manager handles browser lifecycle)
with ScraperService(headless=True) as service:
    # Scrape shops
    shops = service.get_shops()

    # Scrape leaflets
    leaflets = service.get_leaflets("biedronka")

    # Scrape offers
    offers = service.get_offers("biedronka", leaflets[0])

    # Search products
    results = service.search("kawa")
```

### Using Examples

The `examples/` directory contains ready-to-use scripts:

```bash
# Scrape a single shop (using uv - recommended)
uv run python examples/01_scrape_single_shop.py

# Scrape multiple shops
uv run python examples/02_scrape_multiple_shops.py

# Analyze data
uv run python examples/03_analyze_data.py

# Search products
uv run python examples/04_search_offers.py
```

---

## CLI Commands

### scrape-shops

Extract all shops from blix.pl.

```bash
uv run python -m src.cli scrape-shops [OPTIONS]

Options:
  --headless    Run in headless mode (no browser UI)
```

**Example:**
```bash
uv run python -m src.cli scrape-shops --headless
```

**Output:**
- `data/shops/shops.json` - All shops
- `data/shops/{slug}.json` - Individual shop files

---

### scrape-leaflets

Get all leaflets for a specific shop.

```bash
uv run python -m src.cli scrape-leaflets <SHOP> [OPTIONS]

Arguments:
  SHOP              Shop slug (e.g., 'biedronka')

Options:
  --headless       Run in headless mode
```

**Example:**
```bash
uv run python -m src.cli scrape-leaflets biedronka --headless
```

**Output:**
- `data/leaflets/{shop}/{id}.json` - Individual leaflet files

---

### scrape-offers

Extract offers from a specific leaflet.

```bash
uv run python -m src.cli scrape-offers <SHOP> <LEAFLET_ID> [OPTIONS]

Arguments:
  SHOP              Shop slug
  LEAFLET_ID        Leaflet ID number

Options:
  --headless       Run in headless mode
```

**Example:**
```bash
uv run python -m src.cli scrape-offers biedronka 457727 --headless
```

**Output:**
- `data/offers/{id}_offers.json` - Offers for the leaflet

---

### scrape-full-shop

Scrape all data for a shop (leaflets, offers, keywords).

```bash
uv run python -m src.cli scrape-full-shop <SHOP> [OPTIONS]

Arguments:
  SHOP              Shop slug

Options:
  --active-only    Only scrape active leaflets
  --headless       Run in headless mode
```

**Example:**
```bash
uv run python -m src.cli scrape-full-shop biedronka --active-only --headless
```

---

### search

Search for products across all shops.

```bash
uv run python -m src.cli search <QUERY> [OPTIONS]

Arguments:
  QUERY             Search query (e.g., 'kawa')

Options:
  --headless       Run in headless mode
  --all            Show all results (default: limit to 20)
  --no-filter      Don't filter by product name
```

**Example:**
```bash
uv run python -m src.cli search kawa --all
```

---

### list-shops

Display all scraped shops.

```bash
uv run python -m src.cli list-shops
```

---

### list-leaflets

Display leaflets for a shop.

```bash
uv run python -m src.cli list-leaflets <SHOP> [OPTIONS]

Options:
  --active-only    Only show active leaflets
```

---

### config

Show current configuration.

```bash
uv run python -m src.cli config
```

---

### fields-list

List available fields for an entity type. Use this to see what fields are available for use with the `--fields` and `--exclude` options.

```bash
uv run python -m src.cli fields-list <ENTITY> [OPTIONS]

Arguments:
  ENTITY          Entity type (shop, leaflet, offer, search_result, keyword)
```

**Examples:**
```bash
# List all fields for shops
uv run python -m src.cli fields-list shop

# List all fields for offers
uv run python -m src.cli fields-list offer

# List all fields for search results
uv run python -m src.cli fields-list search_result
```

---

## Common CLI Options

The following options are available for most scrape commands:

| Option | Shortcut | Description |
|--------|----------|-------------|
| `--headless` | - | Run browser in headless mode (faster, no UI) |
| `--save` | `-s` | Save results to JSON file |
| `--output` | `-o` | Custom output file path (default: `./data/`) |
| `--dated-dirs` | - | Save to year/month/day subdirectories |
| `--fields` | - | Include only specific fields (comma-separated) |
| `--exclude` | - | Exclude specific fields (comma-separated) |

**Note**: `--fields` and `--exclude` cannot be used together.

---

## JSON Export

Save scraped data to JSON files with optional field filtering:

```bash
# Save all shops to JSON
uv run python -m src.cli scrape-shops --save

# Save to custom output path
uv run python -m src.cli scrape-shops --save --output ./my-data/shops.json

# Save with dated directory structure
uv run python -m src.cli scrape-shops --save --dated-dirs

# Export offers without large image URLs
uv run python -m src.cli scrape-offers biedronka 457727 --exclude image_url --save
```

### JSON Export Metadata

Exported JSON files include metadata:

```json
{
  "metadata": {
    "export_time": "2026-03-07T10:30:00Z",
    "tool": "blix-scraper",
    "version": "1.0.0",
    "schema_version": "1.0.0",
    "entity_type": "offers",
    "command": "scrape_offers",
    "parameters": {
      "shop": "biedronka",
      "leaflet_id": 457727
    },
    "record_count": 150,
    "fields": ["name", "price", "image_url", ...],
    "execution_time_ms": 2500,
    "source_urls": ["https://blix.pl/..."]
  },
  "data": [...]
}
```

---

## Field Filtering Examples

Control which fields are included in JSON exports:

```bash
# Include only specific fields (useful for smaller output)
uv run python -m src.cli scrape-shops --fields name,slug --save
uv run python -m src.cli scrape-leaflets biedronka --fields name,valid_from,valid_until --save
uv run python -m src.cli scrape-offers biedronka 457727 --fields name,price --save

# Exclude specific fields (useful for removing large image URLs)
uv run python -m src.cli scrape-shops --exclude logo_url --save
uv run python -m src.cli scrape-offers biedronka 457727 --exclude image_url --save

# Combine field filtering with dated directories
uv run python -m src.cli scrape-leaflets biedronka --fields name,valid_from --save --dated-dirs

# Search with field filtering
uv run python -m src.cli search "kawa" --fields name,price,shop_name --save
```

### Available Entity Types

| Entity Type | Description |
|-------------|-------------|
| `shop` | Shop information (name, slug, logo_url, etc.) |
| `leaflet` | Leaflet details (name, valid_from, valid_until, etc.) |
| `offer` | Product offers (name, price, image_url, etc.) |
| `search_result` | Search results (name, price_pln, shop_name, etc.) |
| `keyword` | Product keywords |
| `full_shop` | Complete shop data (shop, leaflets, offers, keywords) |

---

## Examples

### Example 1: Scrape Biedronka

```bash
# Scrape all Biedronka data
uv run python -m src.cli scrape-full-shop biedronka --active-only --headless
```

### Example 2: Search for Coffee

```bash
# Search for coffee across all shops
uv run python -m src.cli search kawa --all
```

### Example 3: Scrape Multiple Shops

```bash
# Scrape several popular shops
for shop in biedronka lidl kaufland auchan; do
    uv run python -m src.cli scrape-full-shop $shop --active-only --headless
done
```

### Example 4: Save Data to JSON

```bash
# Save shops to JSON with all fields
uv run python -m src.cli scrape-shops --save

# Save only specific fields
uv run python -m src.cli scrape-shops --fields name,slug,leaflet_count --save

# Save to custom location
uv run python -m src.cli scrape-leaflets biedronka --save --output ./my-folder/biedronka-leaflets.json
```

### Example 5: Use Dated Directories

Organize exports by date for easier archival:

```bash
# Save with year/month/day subdirectories
uv run python -m src.cli scrape-full-shop biedronka --save --dated-dirs
# Output: data/2026/03/07/full_shop_biedronka_20260307.json
```

### Example 6: Field Filtering

```bash
# Get only shop names and slugs (for a simple list)
uv run python -m src.cli scrape-shops --fields name,slug --save

# Get offers without image URLs (smaller file size)
uv run python -m src.cli scrape-offers biedronka 457727 --exclude image_url --save

# Get only essential leaflet info
uv run python -m src.cli scrape-leaflets biedronka --fields name,valid_from,valid_until,status --save
```

### Example 7: Combine Multiple Options

```bash
# Field filtering + dated directories
uv run python -m src.cli scrape-leaflets biedronka \
    --fields name,valid_from,valid_until \
    --save \
    --dated-dirs
```

### Example 8: Use Python API

```python
from src.services import ScraperService

# Create service
with ScraperService(headless=True) as service:
    # Scrape a shop
    leaflets = service.get_leaflets("biedronka")

    # Get active leaflets
    active = [l for l in leaflets if l.status.value == "active"]

    # Scrape offers from first active leaflet
    if active:
        offers = service.get_offers("biedronka", active[0])

        # Find cheapest offer
        if offers:
            cheapest = min(offers, key=lambda o: o.price)
            print(f"Cheapest: {cheapest.name} - {cheapest.price} zl")
```

---

## Data Structure

Scraped data is saved in the `data/` directory:

```
data/
├── shops/
│   ├── shops.json              # All shops metadata
│   ├── biedronka.json          # Individual shop
│   └── lidl.json
├── leaflets/
│   ├── biedronka/
│   │   ├── 457727.json         # Individual leaflet
│   │   └── 457728.json
│   └── lidl/
│       └── 123456.json
├── offers/
│   ├── 457727_offers.json      # Offers for leaflet 457727
│   └── 457728_offers.json
└── keywords/
    └── 457727_keywords.json    # Keywords for leaflet 457727
```

### Shop JSON Structure

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

### Leaflet JSON Structure

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

### Offer JSON Structure

```json
{
  "leaflet_id": 457727,
  "name": "Kawa mielona 250g",
  "price": 12.99,
  "image_url": "https://imgproxy.blix.pl/...",
  "page_number": 3,
  "position_x": 0.25,
  "position_y": 0.35,
  "width": 0.15,
  "height": 0.1,
  "valid_from": "2025-10-29T00:00:00Z",
  "valid_until": "2025-11-05T23:59:59Z"
}
```

---

## Troubleshooting

### ChromeDriver Issues

**Problem**: "ChromeDriver version mismatch" error

**Solution**:
```bash
# The webdriver-manager should auto-download the correct version
# Just restart the scraper
uv run python -m src.cli scrape-shops
```

### Element Not Found

**Problem**: Scraping fails with "element not found" error

**Causes**:
- Website structure changed
- Network issues
- Anti-bot protection triggered

**Solutions**:
1. Check if the website is accessible in your browser
2. Increase delays in `.env`
3. Check for captcha or other protection
4. Update the scraper selectors

### Slow Scraping

**Problem**: Scraping takes too long

**Solutions**:
1. Use headless mode: `--headless`
2. Reduce delays: `REQUEST_DELAY_MIN=1.0`
3. Only scrape active leaflets: `--active-only`
4. Use a faster network connection

### Import Errors

**Problem**: "Module not found" error

**Solutions**:
```bash
# Make sure you're in the project root
cd /path/to/blix-scraper

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Errors

**Problem**: "Permission denied" when creating files

**Solutions**:
```bash
# Check directory permissions
ls -la data/

# Create data directory if needed
mkdir -p data

# Fix permissions if needed
chmod 755 data/
```

### Memory Issues

**Problem**: Out of memory during scraping

**Solutions**:
1. Use headless mode
2. Scrape one shop at a time
3. Increase system swap space
4. Restart the scraper periodically

---

## Getting Help

If you encounter issues not covered here:

1. **Check the examples**: See `examples/` directory for working code
2. **Read the documentation**: See `docs/` directory
3. **Check existing issues**: GitHub Issues page
4. **Ask questions**: Open a new GitHub Issue

---

## Next Steps

- [Examples](../examples/README.md) - Practical example scripts
- [Developer Guide](developer-guide.md) - Contributing and development
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - System architecture
