"""
Example: Scrape all data for a single shop.

This script demonstrates:
- Scraping shop leaflets
- Extracting offers and keywords
- Saving data to JSON files

Usage:
    python examples/01_scrape_single_shop.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import ScraperOrchestrator
from src.config import settings
from src.logging_config import setup_logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Setup logging and console
setup_logging()
console = Console()


def main():
    """
    Scrape all data for a single shop (Biedronka).

    This example shows how to:
    1. Create a ScraperOrchestrator instance
    2. Scrape leaflets for a shop
    3. Scrape offers and keywords for each active leaflet
    4. Handle errors gracefully
    """
    shop_slug = "biedronka"

    console.print(f"\n[bold cyan]Scraping {shop_slug}...[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Create orchestrator with headless mode for faster execution
        with ScraperOrchestrator(headless=True) as orchestrator:
            # Task 1: Scrape all leaflets for the shop
            task1 = progress.add_task("Fetching leaflets...", total=None)
            leaflets = orchestrator.scrape_shop_leaflets(shop_slug)
            progress.update(task1, completed=True)

            console.print(f"Found {len(leaflets)} leaflets\n")

            # Filter to active leaflets only
            active_leaflets = [l for l in leaflets if l.is_active_now()]
            console.print(f"Active leaflets: {len(active_leaflets)}\n")

            # Task 2: Scrape offers and keywords for each active leaflet
            for i, leaflet in enumerate(active_leaflets, 1):
                task2 = progress.add_task(
                    f"[{i}/{len(active_leaflets)}] Scraping leaflet {leaflet.leaflet_id}...",
                    total=None
                )

                try:
                    offers, keywords = orchestrator.scrape_full_leaflet(
                        shop_slug,
                        leaflet.leaflet_id
                    )

                    console.print(
                        f"  Leaflet {leaflet.leaflet_id}: "
                        f"{len(offers)} offers, {len(keywords)} keywords"
                    )

                except Exception as e:
                    console.print(
                        f"  [red]Failed to scrape leaflet {leaflet.leaflet_id}: {e}[/red]"
                    )

                progress.update(task2, completed=True)

    console.print("\n[bold green]Scraping completed![/bold green]")
    console.print(f"\nData saved to: [cyan]{settings.data_dir}[/cyan]")


if __name__ == "__main__":
    main()
