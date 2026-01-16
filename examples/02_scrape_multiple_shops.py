"""
Example: Scrape multiple shops in sequence.

This script demonstrates:
- Scraping multiple shops
- Error handling for each shop
- Progress tracking across all shops
- Statistics collection and display

Usage:
    python examples/02_scrape_multiple_shops.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import ScraperOrchestrator
from src.config import settings
from src.logging_config import setup_logging
from rich.console import Console
from rich.table import Table

setup_logging()
console = Console()


def main():
    """
    Scrape multiple popular shops with error handling.

    This example shows how to:
    1. Define a list of shops to scrape
    2. Scrape each shop with error handling
    3. Collect statistics for all shops
    4. Display a summary table
    """
    shops = ["biedronka", "lidl", "kaufland", "auchan"]

    console.print("\n[bold cyan]Scraping Multiple Shops[/bold cyan]\n")

    all_stats = []

    with ScraperOrchestrator(headless=True) as orchestrator:
        for shop in shops:
            console.print(f"\n[yellow]Processing {shop}...[/yellow]")

            try:
                stats = orchestrator.scrape_all_shop_data(
                    shop,
                    active_only=True
                )
                all_stats.append(stats)

                console.print(
                    f"✓ {shop}: {stats['leaflets_count']} leaflets, "
                    f"{stats['offers_count']} offers"
                )

            except Exception as e:
                console.print(f"✗ [red]Failed to scrape {shop}: {e}[/red]")
                continue

    # Display summary table
    if all_stats:
        console.print("\n[bold green]Summary[/bold green]\n")

        table = Table(title="Scraping Results")
        table.add_column("Shop", style="cyan")
        table.add_column("Leaflets", justify="right", style="yellow")
        table.add_column("Offers", justify="right", style="green")
        table.add_column("Keywords", justify="right", style="magenta")
        table.add_column("Errors", justify="right", style="red")

        for stats in all_stats:
            table.add_row(
                stats['shop_slug'],
                str(stats['leaflets_count']),
                str(stats['offers_count']),
                str(stats['keywords_count']),
                str(len(stats['errors']))
            )

        console.print(table)

        # Calculate totals
        total_leaflets = sum(s['leaflets_count'] for s in all_stats)
        total_offers = sum(s['offers_count'] for s in all_stats)
        total_keywords = sum(s['keywords_count'] for s in all_stats)

        console.print(f"\n[bold]Totals:[/bold]")
        console.print(f"  Leaflets: {total_leaflets}")
        console.print(f"  Offers: {total_offers}")
        console.print(f"  Keywords: {total_keywords}")
    else:
        console.print("\n[yellow]No shops were successfully scraped.[/yellow]")


if __name__ == "__main__":
    main()
