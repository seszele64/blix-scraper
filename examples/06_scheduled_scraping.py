"""
Example: Scheduled scraping with cron-like behavior.

This script demonstrates:
- Periodic scraping
- Detecting new leaflets
- Change detection
- Notifications (console output)

Usage:
    python examples/06_scheduled_scraping.py

Note: Press Ctrl+C to stop the scheduled scraper.
"""

import sys
from pathlib import Path
import json
import time
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import ScraperOrchestrator
from src.domain.entities import Leaflet
from src.config import settings
from src.logging_config import setup_logging
from rich.console import Console

setup_logging()
console = Console()


def get_existing_leaflet_ids(shop_slug: str) -> set[int]:
    """
    Get the IDs of existing leaflets for a shop.

    This function demonstrates:
    - Reading existing leaflet files
    - Extracting leaflet IDs
    - Building a set for fast lookup

    Args:
        shop_slug: The shop to check

    Returns:
        Set of leaflet IDs
    """
    leaflets_dir = settings.data_dir / "leaflets" / shop_slug

    if not leaflets_dir.exists():
        return set()

    existing_ids = set()
    for leaflet_file in leaflets_dir.glob("*.json"):
        try:
            with open(leaflet_file) as f:
                leaflet_data = json.load(f)
                leaflet = Leaflet.model_validate(leaflet_data)
                existing_ids.add(leaflet.leaflet_id)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {leaflet_file.name}: {e}[/yellow]")
            continue

    return existing_ids


def scrape_with_change_detection(shop_slug: str) -> int:
    """
    Scrape a shop and detect new leaflets.

    This function demonstrates:
    - Comparing current and existing data
    - Identifying new and expired leaflets
    - Scraping only new content

    Args:
        shop_slug: The shop to scrape

    Returns:
        Number of new leaflets found
    """
    console.print(f"\n[cyan]Checking {shop_slug}...[/cyan]")

    # Get existing leaflet IDs
    existing_ids = get_existing_leaflet_ids(shop_slug)
    console.print(f"  Existing leaflets: {len(existing_ids)}")

    # Scrape current leaflets
    try:
        with ScraperOrchestrator(headless=True) as orchestrator:
            leaflets = orchestrator.scrape_shop_leaflets(shop_slug)
    except Exception as e:
        console.print(f"[red]Error scraping {shop_slug}: {e}[/red]")
        return 0

    current_ids = {l.leaflet_id for l in leaflets}

    # Detect changes
    new_ids = current_ids - existing_ids
    removed_ids = existing_ids - current_ids

    if new_ids:
        console.print(f"[green]✓ Found {len(new_ids)} new leaflets![/green]")

        # Scrape new leaflets
        try:
            with ScraperOrchestrator(headless=True) as orchestrator:
                for leaflet_id in new_ids:
                    console.print(f"  Scraping new leaflet {leaflet_id}...")
                    try:
                        orchestrator.scrape_full_leaflet(shop_slug, leaflet_id)
                        console.print(f"  ✓ Leaflet {leaflet_id} scraped successfully")
                    except Exception as e:
                        console.print(f"  ✗ Failed to scrape leaflet {leaflet_id}: {e}")
        except Exception as e:
            console.print(f"[red]Error in new leaflet scraping: {e}[/red]")
    else:
        console.print("[yellow]No new leaflets found[/yellow]")

    if removed_ids:
        console.print(f"[yellow]⚠ {len(removed_ids)} leaflets expired or removed[/yellow]")

    return len(new_ids)


def main():
    """
    Main entry point for scheduled scraping.

    This example shows how to:
    1. Define a list of shops to monitor
    2. Set up a scraping interval
    3. Run periodic checks with change detection
    4. Handle graceful shutdown
    """
    shops = ["biedronka", "lidl", "kaufland"]
    interval_minutes = 60  # Check every hour

    console.print("[bold cyan]Starting Scheduled Scraper[/bold cyan]")
    console.print(f"Interval: Every {interval_minutes} minutes")
    console.print(f"Shops: {', '.join(shops)}")
    console.print("Press Ctrl+C to stop\n")

    try:
        while True:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"\n[bold]--- Check at {timestamp} ---[/bold]")

            total_new = 0
            for shop in shops:
                try:
                    new_count = scrape_with_change_detection(shop)
                    total_new += new_count
                except Exception as e:
                    console.print(f"[red]Error processing {shop}: {e}[/red]")

            if total_new > 0:
                console.print(f"\n[bold green]✓ Found {total_new} new leaflets total[/bold green]")
            else:
                console.print("\n[yellow]No changes detected[/yellow]")

            # Wait for next check
            console.print(f"\nSleeping for {interval_minutes} minutes...")
            console.print("Press Ctrl+C to stop early.\n")
            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]Scheduled scraper stopped by user[/bold yellow]")


if __name__ == "__main__":
    main()
