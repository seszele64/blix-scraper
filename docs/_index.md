---
title: Documentation Index
description: Navigation index for blix-scraper documentation
category: documentation
tags:
  - documentation
  - index
  - navigation
  - guide
created: 2026-01-16
updated: 2026-01-16
---

# Documentation Index

Welcome to the blix-scraper documentation. This index provides quick access to all documentation resources.

## Quick Links

| Topic | Description | Link |
|-------|-------------|------|
| 🚀 **Quick Start** | Get up and running in 5 minutes | [User Guide](user-guide.md#quick-start) |
| 📦 **Installation** | Complete installation guide | [User Guide](user-guide.md#installation) |
| 💻 **CLI Usage** | Command-line interface reference | [User Guide](user-guide.md#cli-commands) |
| 📝 **Examples** | Practical example scripts | [Examples README](../examples/README.md) |
| 🛠️ **Development** | Contributing and coding standards | [Developer Guide](developer-guide.md) |
| 📚 **API Reference** | Complete API documentation | [API Reference](api-reference.md) |
| 🏗️ **Architecture** | System architecture overview | [Architecture](architecture.md) |
| 📊 **Domain Model** | Data model documentation | [Domain Model](domain-model.md) |
| 🧪 **Testing** | Testing best practices | [Testing Best Practices](../.specify/memory/testing-best-practices.md) |

## Documentation Overview

### For Users

If you're new to blix-scraper, start here:

1. **[User Guide](user-guide.md)** - Complete guide for using blix-scraper
   - Installation instructions
   - Basic usage patterns
   - CLI command reference
   - Troubleshooting common issues

2. **[Examples](../examples/README.md)** - Ready-to-use example scripts
   - Scrape single/multiple shops
   - Analyze data
   - Search products
   - Export to CSV

### For Developers

If you want to contribute or extend blix-scraper:

1. **[Developer Guide](developer-guide.md)** - Contribution guidelines
   - Development setup
   - Coding standards
   - Testing requirements
   - Release process

2. **[API Reference](api-reference.md)** - Complete API documentation
   - Module documentation
   - Function signatures
   - Class interfaces
   - Code examples

### For Architects

If you want to understand the system design:

1. **[Architecture](architecture.md)** - System architecture
   - High-level design
   - Component relationships
   - Technology choices
   - Design patterns

2. **[Domain Model](domain-model.md)** - Data model
   - Entity definitions
   - Validation rules
   - Storage patterns

3. **[Implementation Patterns](implementation-patterns.md)** - Code patterns
   - Selenium setup
   - Scraper patterns
   - Testing strategies

## Topic Index

### Getting Started

| Topic | Description | Link |
|-------|-------------|------|
| Installation | How to install blix-scraper | [Link](user-guide.md#installation) |
| Configuration | Setting up configuration | [Link](user-guide.md#configuration) |
| First Scrape | Running your first scrape | [Link](user-guide.md#quick-start) |

### Core Concepts

| Topic | Description | Link |
|-------|-------------|------|
| Scraping | How scraping works | [Link](user-guide.md#basic-usage) |
| Data Structure | JSON file structure | [Link](user-guide.md#data-structure) |
| Search | Product search functionality | [Link](user-guide.md#cli-commands) |

### CLI Commands

| Command | Description | Link |
|---------|-------------|------|
| scrape-shops | Extract all shops | [Link](user-guide.md#scrape-shops) |
| scrape-leaflets | Get leaflets for a shop | [Link](user-guide.md#scrape-leaflets) |
| scrape-offers | Extract offers from leaflet | [Link](user-guide.md#scrape-offers) |
| search | Search for products | [Link](user-guide.md#search) |

### Development

| Topic | Description | Link |
|-------|-------------|------|
| Setup | Development environment | [Link](developer-guide.md#development-setup) |
| Structure | Project structure | [Link](developer-guide.md#project-structure) |
| Standards | Coding standards | [Link](developer-guide.md#coding-standards) |
| Testing | Writing tests | [Link](developer-guide.md#testing) |
| Contributing | Pull request process | [Link](developer-guide.md#contributing) |

### API Reference

| Topic | Description | Link |
|-------|-------------|------|
| CLI | CLI module | [Link](api-reference.md#cli-module) |
| Config | Configuration | [Link](api-reference.md#config-module) |
| Entities | Domain models | [Link](api-reference.md#domain-entities) |
| Orchestrator | Main orchestrator | [Link](api-reference.md#orchestrator) |
| Scrapers | Scraper classes | [Link](api-reference.md#scrapers) |
| Storage | Data storage | [Link](api-reference.md#storage) |
| WebDriver | Browser management | [Link](api-reference.md#webdriver) |

## File Reference

### Source Files

| File | Description |
|------|-------------|
| [`src/orchestrator.py`](../src/orchestrator.py) | Main orchestrator class |
| [`src/config.py`](../src/config.py) | Configuration management |
| [`src/domain/entities.py`](../src/domain/entities.py) | Pydantic models |
| [`src/cli/__init__.py`](../src/cli/__init__.py) | CLI interface |
| [`src/scrapers/base.py`](../src/scrapers/base.py) | Base scraper class |

### Documentation Files

| File | Description |
|------|-------------|
| [`docs/user-guide.md`](user-guide.md) | User-facing documentation |
| [`docs/developer-guide.md`](developer-guide.md) | Developer documentation |
| [`docs/api-reference.md`](api-reference.md) | API documentation |
| [`docs/architecture.md`](architecture.md) | Architecture documentation |
| [`docs/domain-model.md`](domain-model.md) | Domain model documentation |

### Example Files

| File | Description |
|------|-------------|
| [`examples/01_scrape_single_shop.py`](../examples/01_scrape_single_shop.py) | Single shop scraping |
| [`examples/02_scrape_multiple_shops.py`](../examples/02_scrape_multiple_shops.py) | Multiple shops |
| [`examples/03_analyze_data.py`](../examples/03_analyze_data.py) | Data analysis |
| [`examples/04_search_offers.py`](../examples/04_search_offers.py) | Product search |
| [`examples/05_export_csv.py`](../examples/05_export_csv.py) | CSV export |
| [`examples/06_scheduled_scraping.py`](../examples/06_scheduled_scraping.py) | Scheduled scraping |

## Common Tasks

### Task 1: Scrape a Shop

1. Read the [User Guide](user-guide.md)
2. Run: `python -m src.cli scrape-full-shop <shop>`
3. See example: [`01_scrape_single_shop.py`](../examples/01_scrape_single_shop.py)

### Task 2: Search Products

1. Read about [search functionality](user-guide.md#search)
2. Run: `python -m src.cli search <query>`
3. See example: [`04_search_offers.py`](../examples/04_search_offers.py)

### Task 3: Analyze Data

1. Learn about [data structure](user-guide.md#data-structure)
2. Run analysis: `python examples/03_analyze_data.py`
3. Export: `python examples/05_export_csv.py`

### Task 4: Contribute Code

1. Read [Developer Guide](developer-guide.md)
2. Set up [development environment](developer-guide.md#development-setup)
3. Follow [coding standards](developer-guide.md#coding-standards)
4. Submit [pull request](developer-guide.md#contributing)

## Additional Resources

### External Links

- [GitHub Repository](https://github.com/yourusername/blix-scraper)
- [Issue Tracker](https://github.com/yourusername/blix-scraper/issues)
- [PyPI Package](https://pypi.org/project/blix-scraper/)

### Related Documentation

- [Python Documentation](https://docs.python.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)

## Getting Help

### Self-Help

1. **Troubleshooting**: See [User Guide - Troubleshooting](user-guide.md#troubleshooting)
2. **Examples**: Check [`examples/`](../examples/) directory
3. **API**: Search in [API Reference](api-reference.md)

### Getting Support

1. **Check existing issues**: [GitHub Issues](https://github.com/yourusername/blix-scraper/issues)
2. **Ask questions**: Open a new issue with question tag
3. **Report bugs**: Open a new issue with bug label

## Version Information

| Information | Value |
|-------------|-------|
| Current Version | See [`pyproject.toml`](../pyproject.toml) |
| Python Version | 3.11+ |
| Last Updated | 2026-01-16 |
| Documentation Status | Complete |

---

## Navigation

[← Back to Project Root](../README.md) | [User Guide →](user-guide.md)
