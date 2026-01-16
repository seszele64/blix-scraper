"""
Example: Search for products and analyze results.

This script demonstrates:
- Using the search engine
- Analyzing search results
- Finding best deals
- Cross-shop comparison
- Using FieldFilter for selective data export

Usage:
    python examples/07_search_products.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import ScraperOrchestrator
from src.storage.field_filter import FieldFilter
from src.logging_config import setup_logging
from rich.console import Console
from rich.table import Table
from collections import Counter

setup_logging()
console = Console()


def search_and_analyze(query: str, field_filter: FieldFilter = None):
    """
    Search for products and analyze the results.

    This function demonstrates:
    - Using the search_products method
    - Filtering results by name
    - Analyzing results by brand, shop, and price
    - Displaying formatted results

    Args:
        query: The search query
        field_filter: Optional filter for what data to save
    """
    console.print(f"\n[bold cyan]Searching for: {query}[/bold cyan]\n")

    with ScraperOrchestrator(headless=True) as orchestrator:
        # Search for products (filter_by_name=True by default)
        results = orchestrator.search_products(
            query,
            filter_by_name=True,
            field_filter=field_filter
        )

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    console.print(f"Found {len(results)} results\n")

    # Analysis 1: Best deals (offers with prices)
    results_with_price = [r for r in results if r.price_pln is not None]

    if results_with_price:
        console.print("[bold]Top 10 Cheapest Products:[/bold]\n")

        cheapest = sorted(results_with_price, key=lambda r: r.price_pln)[:10]

        table = Table()
        table.add_column("Product", style="green")
        table.add_column("Shop", style="magenta")
        table.add_column("Brand", style="cyan")
        table.add_column("Price", justify="right", style="yellow")
        table.add_column("Leaflet", justify="right")

        for result in cheapest:
            name_display = result.name[:50] + "..." if len(result.name) > 50 else result.name
            table.add_row(
                name_display,
                result.shop_name or "Unknown",
                result.brand_name or "-",
                f"{result.price_pln:.2f} zł",
                str(result.leaflet_id)
            )

        console.print(table)

    # Analysis 2: Results by brand
    console.print("\n[bold]Results by Brand:[/bold]\n")

    brands = Counter(r.brand_name for r in results if r.brand_name)

    if brands:
        table = Table()
        table.add_column("Brand", style="cyan")
        table.add_column("Count", justify="right", style="yellow")
        table.add_column("Avg Price", justify="right", style="green")

        for brand, count in brands.most_common(10):
            if results_with_price:
                brand_results = [r for r in results_with_price if r.brand_name == brand]
                if brand_results:
                    avg_price = sum(r.price_pln for r in brand_results) / len(brand_results)
                    table.add_row(brand, str(count), f"{avg_price:.2f} zł")
                else:
                    table.add_row(brand, str(count), "N/A")
            else:
                table.add_row(brand, str(count), "N/A")

        console.print(table)

    # Analysis 3: Results by shop
    console.print("\n[bold]Results by Shop:[/bold]\n")

    shops = Counter(r.shop_name for r in results if r.shop_name)

    if shops:
        table = Table()
        table.add_column("Shop", style="magenta")
        table.add_column("Count", justify="right", style="yellow")
        table.add_column("Avg Price", justify="right", style="green")
        table.add_column("Min Price", justify="right", style="cyan")

        for shop, count in shops.most_common():
            if results_with_price:
                shop_results = [r for r in results_with_price if r.shop_name == shop]
                if shop_results:
                    avg_price = sum(r.price_pln for r in shop_results) / len(shop_results)
                    min_price = min(r.price_pln for r in shop_results)
                    table.add_row(
                        shop,
                        str(count),
                        f"{avg_price:.2f} zł",
                        f"{min_price:.2f} zł"
                    )
                else:
                    table.add_row(shop, str(count), "N/A", "N/A")
            else:
                table.add_row(shop, str(count), "N/A", "N/A")

        console.print(table)

    # Analysis 4: Price statistics
    if results_with_price:
        prices = [r.price_pln for r in results_with_price]

        console.print("\n[bold]Price Statistics:[/bold]")
        console.print(f"  Minimum price: {min(prices):.2f} zł")
        console.print(f"  Maximum price: {max(prices):.2f} zł")
        console.print(f"  Average price: {sum(prices)/len(prices):.2f} zł")
        console.print(f"  Results with price: {len(results_with_price)}/{len(results)}")


def main():
    """
    Main entry point for product search and analysis.

    This example shows how to:
    1. Define search queries
    2. Use different FieldFilter options
    3. Analyze search results
    """
    queries = ["kawa", "mleko", "chleb", "masło"]

    # Define different field filters for different use cases
    filter_base = FieldFilter.with_dates()  # Includes date fields
    filter_minimal = FieldFilter.minimal()  # Only essential fields
    filter_custom = FieldFilter.custom("name", "price", "shop_name", "brand_name")  # Custom selection
    filter_extended = FieldFilter.extended("image_url", "leaflet_id")  # Extended fields

    # Choose which filter to use (change this to experiment)
    chosen_filter = filter_base  # You can change this to any of the filters above

    console.print("[bold cyan]Product Search and Analysis[/bold cyan]")
    console.print(f"Using filter: {type(chosen_filter).__name__}\n")

    for query in queries:
        search_and_analyze(query, field_filter=chosen_filter)
        console.print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
