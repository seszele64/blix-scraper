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

from src.services.scraper_service import ScraperService
from src.logging_config import setup_logging
from rich.console import Console
from rich.table import Table

setup_logging()
console = Console()


def scrape_shop_data(service: ScraperService, shop_slug: str, active_only: bool = True) -> dict:
    """Scrape all data for a single shop and collect statistics.

    Args:
        service: Active ScraperService instance
        shop_slug: Shop identifier (e.g., 'biedronka')
        active_only: Only scrape active leaflets

    Returns:
        Dictionary with scraping statistics
    """
    leaflets = service.get_leaflets(shop_slug)

    if active_only:
        leaflets = [l for l in leaflets if l.is_active_now()]

    offers_count = 0
    keywords_count = 0
    errors = []

    for leaflet in leaflets:
        try:
            offers = service.get_offers(shop_slug, leaflet)
            keywords = service.get_keywords(shop_slug, leaflet)
            offers_count += len(offers)
            keywords_count += len(keywords)
        except Exception as e:
            errors.append(f"{leaflet.leaflet_id}: {e}")

    return {
        "shop_slug": shop_slug,
        "leaflets_count": len(leaflets),
        "offers_count": offers_count,
        "keywords_count": keywords_count,
        "errors": errors,
    }


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

    with ScraperService(headless=True) as service:
        for shop in shops:
            console.print(f"\n[yellow]Processing {shop}...[/yellow]")

            try:
                stats = scrape_shop_data(service, shop, active_only=True)
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