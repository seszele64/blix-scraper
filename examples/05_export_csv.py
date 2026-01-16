"""
Example: Export scraped data to CSV.

This script demonstrates:
- Converting JSON data to CSV format
- Data export for use in Excel/Google Sheets
- Creating reports from scraped data

Usage:
    python examples/05_export_csv.py
"""

import sys
from pathlib import Path
import json
import csv
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.entities import Shop, Leaflet, Offer
from src.config import settings
from rich.console import Console

console = Console()


def export_shops_csv(output_file: Path):
    """
    Export all shops to a CSV file.

    This function demonstrates:
    - Loading shop data from JSON
    - Writing to CSV format
    - Handling datetime serialization

    Args:
        output_file: Path where the CSV file will be saved
    """
    shops_file = settings.data_dir / "shops" / "shops.json"

    if not shops_file.exists():
        console.print("[yellow]No shops data found.[/yellow]")
        console.print("Please run: python -m src.cli scrape-shops")
        return

    try:
        with open(shops_file) as f:
            shops_data = json.load(f)

        shops = [Shop.model_validate(s) for s in shops_data]

        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header row
            writer.writerow([
                'Slug',
                'Name',
                'Leaflet Count',
                'Is Popular',
                'Logo URL',
                'Category',
                'Scraped At'
            ])

            # Write data rows
            for shop in shops:
                writer.writerow([
                    shop.slug,
                    shop.name,
                    shop.leaflet_count,
                    'Yes' if shop.is_popular else 'No',
                    str(shop.logo_url) if shop.logo_url else '',
                    shop.category or '',
                    shop.scraped_at.isoformat() if shop.scraped_at else ''
                ])

        console.print(f"✓ Exported {len(shops)} shops to {output_file}")

    except Exception as e:
        console.print(f"[red]Error exporting shops: {e}[/red]")


def export_offers_csv(shop_slug: str, output_file: Path):
    """
    Export all offers for a specific shop to a CSV file.

    This function demonstrates:
    - Loading all leaflets for a shop
    - Loading offers from each leaflet
    - Combining data for export

    Args:
        shop_slug: The shop to export offers for
        output_file: Path where the CSV file will be saved
    """
    all_offers = []

    # Load all leaflets for the shop
    leaflets_dir = settings.data_dir / "leaflets" / shop_slug

    if not leaflets_dir.exists():
        console.print(f"[yellow]No leaflets found for {shop_slug}.[/yellow]")
        console.print(f"Please run: python -m src.cli scrape-leaflets {shop_slug}")
        return

    try:
        for leaflet_file in leaflets_dir.glob("*.json"):
            with open(leaflet_file) as f:
                leaflet_data = json.load(f)
                leaflet = Leaflet.model_validate(leaflet_data)

            # Load offers for this leaflet
            offers_file = settings.data_dir / "offers" / f"{leaflet.leaflet_id}_offers.json"
            if not offers_file.exists():
                continue

            with open(offers_file) as f:
                offers_data = json.load(f)

            offers = [Offer.model_validate(o) for o in offers_data]
            all_offers.extend(offers)

        if not all_offers:
            console.print("[yellow]No offers found to export.[/yellow]")
            return

        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header row
            writer.writerow([
                'Leaflet ID',
                'Product Name',
                'Price',
                'Page Number',
                'Valid From',
                'Valid Until',
                'Image URL'
            ])

            # Write data rows
            for offer in all_offers:
                writer.writerow([
                    offer.leaflet_id,
                    offer.name,
                    str(offer.price) if offer.price else '',
                    offer.page_number,
                    offer.valid_from.isoformat() if offer.valid_from else '',
                    offer.valid_until.isoformat() if offer.valid_until else '',
                    str(offer.image_url) if offer.image_url else ''
                ])

        console.print(f"✓ Exported {len(all_offers)} offers to {output_file}")

    except Exception as e:
        console.print(f"[red]Error exporting offers: {e}[/red]")


def main():
    """
    Main entry point for CSV export.

    This example shows how to:
    1. Create an exports directory
    2. Export shops to CSV
    3. Export offers for a specific shop
    """
    console.print("\n[bold cyan]Exporting Data to CSV[/bold cyan]\n")

    # Create exports directory
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    # Export shops
    shops_csv = exports_dir / "shops.csv"
    export_shops_csv(shops_csv)

    # Export offers for Biedronka
    biedronka_csv = exports_dir / "biedronka_offers.csv"
    export_offers_csv("biedronka", biedronka_csv)

    console.print(f"\n[bold green]Export completed![/bold green]")
    console.print(f"Files saved to: [cyan]{exports_dir}/[/cyan]")


if __name__ == "__main__":
    main()
