"""
Example: Search for specific products across shops.

This script demonstrates:
- Searching offers by keyword
- Cross-shop comparison
- Price comparison
- Interactive search functionality

Usage:
    python examples/04_search_offers.py
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.entities import Offer, Leaflet
from src.config import settings
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()


def search_offers(keyword: str) -> list[tuple[Offer, str, Leaflet]]:
    """
    Search for offers containing a keyword across all shops.

    This function demonstrates:
    - Iterating through all scraped shops
    - Loading leaflets and offers for each shop
    - Filtering offers by product name

    Args:
        keyword: The search term to look for

    Returns:
        List of tuples containing (offer, shop_slug, leaflet)
    """
    results = []
    keyword_lower = keyword.lower()

    # Iterate through all shops
    leaflets_dir = settings.data_dir / "leaflets"

    if not leaflets_dir.exists():
        console.print("[yellow]No scraped data found.[/yellow]")
        console.print("Please run some scraping commands first.")
        return []

    for shop_dir in leaflets_dir.iterdir():
        if not shop_dir.is_dir():
            continue

        shop_slug = shop_dir.name

        # Load each leaflet in this shop
        for leaflet_file in shop_dir.glob("*.json"):
            try:
                with open(leaflet_file) as f:
                    leaflet_data = json.load(f)
                    leaflet = Leaflet.model_validate(leaflet_data)

                # Load offers for this leaflet
                offers_file = settings.data_dir / "offers" / f"{leaflet.leaflet_id}_offers.json"
                if not offers_file.exists():
                    continue

                with open(offers_file) as f:
                    offers_data = json.load(f)

                # Search in offers
                for offer_data in offers_data:
                    offer = Offer.model_validate(offer_data)

                    if keyword_lower in offer.name.lower():
                        results.append((offer, shop_slug, leaflet))

            except Exception as e:
                console.print(f"[red]Error processing {leaflet_file.name}: {e}[/red]")
                continue

    return results


def main():
    """
    Main entry point for interactive product search.

    This example shows how to:
    1. Get search term from user
    2. Search across all scraped data
    3. Display results in a formatted table
    4. Show price statistics
    """
    console.print("\n[bold cyan]Product Search[/bold cyan]\n")

    # Get search term from user
    keyword = Prompt.ask("Enter product name to search for")

    if not keyword.strip():
        console.print("[yellow]Please enter a valid search term.[/yellow]")
        return

    console.print(f"\n[yellow]Searching for '{keyword}'...[/yellow]\n")

    results = search_offers(keyword)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        console.print("Try searching for different products (e.g., 'kawa', 'mleko', 'chleb').")
        return

    console.print(f"Found {len(results)} offers\n")

    # Display results
    table = Table(title=f"Search Results for '{keyword}'")
    table.add_column("Shop", style="cyan")
    table.add_column("Product", style="green")
    table.add_column("Price", justify="right", style="yellow")
    table.add_column("Valid Until", style="magenta")

    # Sort by price (offers without price at end)
    results_sorted = sorted(
        results,
        key=lambda x: (x[0].price is None, x[0].price if x[0].price else 0)
    )

    for offer, shop_slug, leaflet in results_sorted:
        price_str = f"{offer.price} zł" if offer.price else "N/A"
        valid_until = leaflet.valid_until.strftime("%Y-%m-%d")
        name_display = offer.name[:60] + "..." if len(offer.name) > 60 else offer.name

        table.add_row(
            shop_slug,
            name_display,
            price_str,
            valid_until
        )

    console.print(table)

    # Show price statistics if available
    offers_with_price = [r[0] for r in results if r[0].price is not None]

    if offers_with_price:
        prices = [o.price for o in offers_with_price]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)

        console.print("\n[bold]Price Statistics:[/bold]")
        console.print(f"  Cheapest: {min_price} zł")
        console.print(f"  Most expensive: {max_price} zł")
        console.print(f"  Average: {avg_price:.2f} zł")
        console.print(f"  Offers with price: {len(offers_with_price)}/{len(results)}")


if __name__ == "__main__":
    main()
