"""
Example: Analyze scraped data.

This script demonstrates:
- Loading scraped data from JSON
- Data analysis
- Finding best deals
- Category statistics

Usage:
    python examples/03_analyze_data.py
"""

import sys
from pathlib import Path
import json
from collections import Counter
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.entities import Shop, Leaflet, Offer, Keyword
from src.config import settings
from rich.console import Console
from rich.table import Table

console = Console()


def load_offers(leaflet_id: int) -> list[Offer]:
    """
    Load offers for a specific leaflet.

    Args:
        leaflet_id: The ID of the leaflet

    Returns:
        List of Offer entities
    """
    offers_file = settings.data_dir / "offers" / f"{leaflet_id}_offers.json"

    if not offers_file.exists():
        console.print(f"[yellow]No offers found for leaflet {leaflet_id}[/yellow]")
        return []

    try:
        with open(offers_file) as f:
            data = json.load(f)

        offers = [Offer.model_validate(o) for o in data]
        return offers

    except Exception as e:
        console.print(f"[red]Error loading offers for leaflet {leaflet_id}: {e}[/red]")
        return []


def load_keywords(leaflet_id: int) -> list[Keyword]:
    """
    Load keywords for a specific leaflet.

    Args:
        leaflet_id: The ID of the leaflet

    Returns:
        List of Keyword entities
    """
    keywords_file = settings.data_dir / "keywords" / f"{leaflet_id}_keywords.json"

    if not keywords_file.exists():
        return []

    try:
        with open(keywords_file) as f:
            data = json.load(f)

        keywords = [Keyword.model_validate(k) for k in data]
        return keywords

    except Exception as e:
        console.print(f"[red]Error loading keywords for leaflet {leaflet_id}: {e}[/red]")
        return []


def analyze_shop(shop_slug: str):
    """
    Analyze all scraped data for a specific shop.

    This function demonstrates:
    - Loading all leaflets for a shop
    - Loading all offers and keywords
    - Analyzing price data
    - Finding popular categories
    - Generating statistics

    Args:
        shop_slug: The slug identifier for the shop
    """
    console.print(f"\n[bold cyan]Analyzing data for: {shop_slug}[/bold cyan]\n")

    # Load leaflets
    leaflets_dir = settings.data_dir / "leaflets" / shop_slug
    if not leaflets_dir.exists():
        console.print(f"[yellow]No data found for shop: {shop_slug}[/yellow]")
        console.print(f"Please run: python -m src.cli scrape-full-shop {shop_slug}")
        return

    leaflet_files = list(leaflets_dir.glob("*.json"))
    console.print(f"Found {len(leaflet_files)} leaflets\n")

    all_offers = []
    all_keywords = []

    for leaflet_file in leaflet_files:
        try:
            with open(leaflet_file) as f:
                leaflet_data = json.load(f)
                leaflet = Leaflet.model_validate(leaflet_data)

            # Load offers and keywords for this leaflet
            offers = load_offers(leaflet.leaflet_id)
            keywords = load_keywords(leaflet.leaflet_id)

            all_offers.extend(offers)
            all_keywords.extend(keywords)

        except Exception as e:
            console.print(f"[red]Error processing {leaflet_file.name}: {e}[/red]")
            continue

    # Analysis 1: Cheapest offers with prices
    console.print("[bold]Top 10 Cheapest Offers:[/bold]\n")

    offers_with_price = [o for o in all_offers if o.price is not None]

    if offers_with_price:
        cheapest = sorted(offers_with_price, key=lambda o: o.price)[:10]

        table = Table()
        table.add_column("Product", style="cyan")
        table.add_column("Price", justify="right", style="green")

        for offer in cheapest:
            price_str = f"{offer.price} zł" if offer.price else "N/A"
            name_display = offer.name[:50] + "..." if len(offer.name) > 50 else offer.name
            table.add_row(name_display, price_str)

        console.print(table)

    else:
        console.print("[yellow]No offers with prices found[/yellow]\n")

    # Analysis 2: Most expensive offers
    console.print("\n[bold]Top 10 Most Expensive Offers:[/bold]\n")

    if offers_with_price:
        most_expensive = sorted(offers_with_price, key=lambda o: o.price, reverse=True)[:10]

        table = Table()
        table.add_column("Product", style="cyan")
        table.add_column("Price", justify="right", style="red")

        for offer in most_expensive:
            price_str = f"{offer.price} zł" if offer.price else "N/A"
            name_display = offer.name[:50] + "..." if len(offer.name) > 50 else offer.name
            table.add_row(name_display, price_str)

        console.print(table)

    # Analysis 3: Popular categories
    console.print("\n[bold]Top 10 Categories:[/bold]\n")

    if all_keywords:
        categories = [
            k.category_path.split('/')[0]
            for k in all_keywords
            if k.category_path
        ]
        category_counts = Counter(categories)

        table = Table()
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right", style="yellow")

        for category, count in category_counts.most_common(10):
            table.add_row(category, str(count))

        console.print(table)

    # Statistics summary
    console.print("\n[bold]Statistics Summary:[/bold]")

    if offers_with_price:
        avg_price = sum(o.price for o in offers_with_price) / len(offers_with_price)
        console.print(f"\n  Total offers: {len(all_offers)}")
        console.print(f"  Offers with price: {len(offers_with_price)}")
        console.print(f"  Average price: {avg_price:.2f} zł")
    else:
        console.print(f"\n  Total offers: {len(all_offers)}")
        console.print(f"  Offers with price: 0")

    console.print(f"\n  Total keywords: {len(all_keywords)}")
    if all_keywords:
        unique_keywords = len(set(k.text for k in all_keywords))
        console.print(f"  Unique keywords: {unique_keywords}")


def main():
    """Main entry point for data analysis."""
    console.print("[bold cyan]Blix Scraper - Data Analysis[/bold cyan]\n")

    # Analyze Biedronka (modify or add more shops as needed)
    analyze_shop("biedronka")


if __name__ == "__main__":
    main()
