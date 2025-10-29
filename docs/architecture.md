# Blix Scraper - Revised System Architecture

## 1. System Overview

### 1.1 Purpose
Lightweight web scraper for blix.pl that extracts:
- Shop information (brands, categories)
- Leaflet metadata (promotional flyers)
- Product offers within leaflets
- Keywords associated with leaflets

**Key Design Decision**: File-based storage (JSON/CSV) instead of database for simplicity and portability.

### 1.2 High-Level Architecture

```
┌─────────────────┐
│  CLI Interface  │ ← Typer-based commands
└────────┬────────┘
         │
┌────────▼────────┐
│  Orchestrator   │ ← Coordinates scraping workflows
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼───┐ ┌────▼────┐ ┌──▼───┐
│ Shop  │ │Leaflet│ │ Offer   │ │Keyword│
│Scraper│ │Scraper│ │ Scraper │ │Scraper│
└───┬───┘ └──┬───┘ └────┬────┘ └──┬───┘
    │        │           │         │
    └────────┴───────────┴─────────┘
             │
    ┌────────▼────────────────┐
    │  Selenium Driver        │
    │  (undetected-chrome)    │
    └────────┬────────────────┘
             │
    ┌────────▼────────┐
    │  HTML Parser    │ ← BeautifulSoup
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  File Storage   │ ← JSON files
    │  (data/*.json)  │
    └─────────────────┘
```

### 1.3 Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| WebDriver | `undetected-chromedriver` | Bypasses anti-bot detection |
| Driver Management | `webdriver-manager` | Auto-handles Chrome version matching |
| HTML Parsing | `BeautifulSoup4` + `lxml` | Robust, flexible parsing |
| Data Validation | `pydantic` v2 | Type safety, validation |
| Storage | JSON files | Simple, portable, version-controllable |
| Testing | `pytest` + fixtures | Realistic HTML test data |
| CLI | `typer` | Modern, type-hinted CLI |
| Logging | `structlog` | Structured logging |

### 1.4 Design Principles

1. **KISS**: File-based storage, no database complexity
2. **Separation of Concerns**: Scrapers, storage, orchestration are independent
3. **Testability**: Real HTML fixtures from actual website
4. **Robustness**: Undetected Chrome handles anti-bot measures
5. **Single Responsibility**: Each scraper handles one entity type

---

## 2. File Storage Structure

```
data/
├── shops/
│   ├── shops.json              # All shops metadata
│   └── shops_by_category.json  # Shops grouped by category
├── leaflets/
│   ├── biedronka/
│   │   ├── 457727.json         # Individual leaflet
│   │   └── 457728.json
│   └── lidl/
│       └── 123456.json
├── offers/
│   ├── 457727_offers.json      # All offers for leaflet 457727
│   └── 457728_offers.json
├── keywords/
│   └── 457727_keywords.json    # Keywords for leaflet 457727
└── cache/
    └── html_cache/             # Optional: cached HTML pages
        └── shops_page.html
```

### 2.1 JSON Schema Examples

**shops.json**:
```json
{
  "shops": [
    {
      "slug": "biedronka",
      "brand_id": 23,
      "name": "Biedronka",
      "logo_url": "https://img.blix.pl/image/brand/thumbnail_23.jpg",
      "category": "Sklepy spożywcze",
      "leaflet_count": 13,
      "is_popular": true,
      "scraped_at": "2025-10-30T12:00:00Z"
    }
  ]
}
```

**457727.json** (leaflet):
```json
{
  "leaflet_id": 457727,
  "shop_slug": "biedronka",
  "name": "Od środy, Z ladą tradycyjną",
  "cover_image_url": "https://imgproxy.blix.pl/image/leaflet/457727/...",
  "url": "https://blix.pl/sklep/biedronka/gazetka/457727/",
  "valid_from": "2025-10-29T00:00:00Z",
  "valid_until": "2025-11-05T23:59:59Z",
  "status": "active",
  "page_count": 12,
  "scraped_at": "2025-10-30T12:05:00Z"
}
```

---

## 3. Non-Functional Requirements

### 3.1 Performance
- Target: Scrape 50 leaflets/hour (with human-like delays)
- Headless mode: Optional for faster scraping
- Caching: Optional HTML caching to reduce requests

### 3.2 Reliability
- Retry logic: 3 attempts with exponential backoff
- Error handling: Graceful failure, log errors, continue
- Data validation: Pydantic validation before saving
- Idempotency: Overwrite existing files (updates)

### 3.3 Observability
- Structured logging with context (shop, leaflet_id)
- Progress bars (tqdm) for long operations
- Error summary at end of scraping session

### 3.4 Maintainability
- Type hints everywhere (`mypy --strict`)
- Real HTML fixtures from actual site
- Documentation in code
- Configuration via YAML/TOML

---

## 4. Security & Ethics

### 4.1 Scraping Ethics
- Respect `robots.txt`
- Human-like delays (2-5s between requests)
- User-Agent: Realistic Chrome user agent
- Run during off-peak hours

### 4.2 Chrome Profile
- Optional: Use persistent Chrome profile
- Cookies/session management handled by undetected-chrome

---

## 5. Deployment Strategy

### 5.1 Development
- Local JSON files in `data/` directory
- Chrome browser installed
- Python virtual environment

### 5.2 Production
- Docker container with Chrome installed
- Mounted volume for `data/` persistence
- Cron job or systemd timer for scheduled runs

**Dockerfile Example**:
```dockerfile
FROM python:3.11-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "-m", "src.cli", "scrape-all"]
```

---

## 6. Future Considerations

### 6.1 Phase 2 Features
- Export to CSV for analysis
- Price history tracking (compare JSON versions)
- Notifications (email/Discord webhook)
- Web UI to browse scraped data

### 6.2 Potential Challenges
- Chrome updates breaking driver
  - **Solution**: webdriver-manager auto-updates
- Anti-bot detection
  - **Solution**: undetected-chromedriver + human delays
- Large data files
  - **Solution**: Split by date/shop, compression