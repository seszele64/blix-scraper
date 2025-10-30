"""CLI interface for Blix scraper."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
import json

from ..logging_config import setup_logging
from ..orchestrator import ScraperOrchestrator
from ..config import settings
from ..storage.json_storage import JSONStorage
from ..domain.entities import Shop, Leaflet, SearchResult

# Setup logging
setup_logging()

# Create Typer app
app = typer.Typer(
    name="blix-scraper",
    help="Web scraper for blix.pl promotional leaflets"
)

console = Console()


@app.command()
def scrape_shops(
    headless: bool = typer.Option(
        False,
        "--headless",
        help="Run browser in headless mode"
    )
):
    """Scrape all shops from blix.pl/sklepy/"""
    console.print("[bold blue]Scraping shops...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching shops...", total=None)
        
        with ScraperOrchestrator(headless=headless) as orchestrator:
            shops = orchestrator.scrape_all_shops()
        
        progress.update(task, completed=True)
    
    # Display results
    table = Table(title="Scraped Shops")
    table.add_column("Slug", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Leaflets", justify="right", style="yellow")
    table.add_column("Popular", justify="center")
    
    for shop in sorted(shops, key=lambda s: s.name):
        table.add_row(
            shop.slug,
            shop.name,
            str(shop.leaflet_count),
            "✓" if shop.is_popular else ""
        )
    
    console.print(table)
    console.print(f"\n[bold green]✓ Scraped {len(shops)} shops[/bold green]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query (e.g., 'kawa')"),
    headless: bool = typer.Option(False, "--headless"),
    show_all: bool = typer.Option(
        False,
        "--all",
        help="Show all results (default: limit to 20)"
    ),
    no_filter: bool = typer.Option(
        False,
        "--no-filter",
        help="Don't filter by product name (show all offers from matching leaflets)"
    )
):
    """Search for products across all shops"""
    console.print(f"[bold blue]Searching for '{query}'...[/bold blue]")
    
    filter_by_name = not no_filter
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Searching...", total=None)
        
        with ScraperOrchestrator(headless=headless) as orchestrator:
            results = orchestrator.search_products(query, filter_by_name=filter_by_name)
        
        progress.update(task, completed=True)
    
    if not results:
        console.print("[yellow]No results found[/yellow]")
        return
    
    # Display filter status
    if filter_by_name:
        console.print(f"[dim](Filtered to products containing '{query}')[/dim]")
    else:
        console.print(f"[dim](Showing all offers from leaflets matching '{query}')[/dim]")
    
    # Display results
    table = Table(title=f"Search Results for '{query}'")
    table.add_column("Product", style="green")
    table.add_column("Brand", style="cyan")
    table.add_column("Price", justify="right", style="yellow")
    table.add_column("Leaflet", justify="right", style="magenta")
    table.add_column("Page", justify="right", style="blue")
    
    # Sort by price
    results_sorted = sorted(
        results,
        key=lambda x: (x.price is None, x.price if x.price else 0)
    )
    
    # Limit display
    display_results = results_sorted if show_all else results_sorted[:20]
    
    for result in display_results:
        price_str = f"{result.price_pln:.2f} zł" if result.price_pln else "N/A"
        
        table.add_row(
            result.name[:50] + "..." if len(result.name) > 50 else result.name,
            result.brand_name or "-",
            price_str,
            str(result.leaflet_id),
            str(result.page_number)
        )
    
    console.print(table)
    
    if not show_all and len(results) > 20:
        console.print(f"\n[yellow]Showing 20 of {len(results)} results. Use --all to see all.[/yellow]")
    
    # Statistics
    console.print(f"\n[bold]Statistics:[/bold]")
    console.print(f"  Total results: {len(results)}")
    
    results_with_price = [r for r in results if r.price_pln is not None]
    if results_with_price:
        prices = [r.price_pln for r in results_with_price]
        console.print(f"  Results with price: {len(results_with_price)}")
        console.print(f"  Cheapest: {min(prices):.2f} zł")
        console.print(f"  Most expensive: {max(prices):.2f} zł")
        console.print(f"  Average: {sum(prices)/len(prices):.2f} zł")
    
    # Unique brands
    brands = set(r.brand_name for r in results if r.brand_name)
    console.print(f"  Unique brands: {len(brands)}")


@app.command()
def scrape_leaflets(
    shop: str = typer.Argument(..., help="Shop slug (e.g., 'biedronka')"),
    headless: bool = typer.Option(False, "--headless")
):
    """Scrape all leaflets for a specific shop"""
    console.print(f"[bold blue]Scraping leaflets for {shop}...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching leaflets...", total=None)
        
        with ScraperOrchestrator(headless=headless) as orchestrator:
            leaflets = orchestrator.scrape_shop_leaflets(shop)
        
        progress.update(task, completed=True)
    
    # Display results
    table = Table(title=f"Leaflets for {shop}")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Valid From", style="magenta")
    table.add_column("Valid Until", style="magenta")
    
    for leaflet in sorted(leaflets, key=lambda l: l.valid_from, reverse=True):
        table.add_row(
            str(leaflet.leaflet_id),
            leaflet.name[:40] + "..." if len(leaflet.name) > 40 else leaflet.name,
            leaflet.status.value,
            leaflet.valid_from.strftime("%Y-%m-%d"),
            leaflet.valid_until.strftime("%Y-%m-%d")
        )
    
    console.print(table)
    console.print(f"\n[bold green]✓ Scraped {len(leaflets)} leaflets[/bold green]")


@app.command()
def scrape_offers(
    shop: str = typer.Argument(..., help="Shop slug"),
    leaflet_id: int = typer.Argument(..., help="Leaflet ID"),
    headless: bool = typer.Option(False, "--headless")
):
    """Scrape offers for a specific leaflet"""
    console.print(
        f"[bold blue]Scraping offers for leaflet {leaflet_id}...[/bold blue]"
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching offers...", total=None)
        
        with ScraperOrchestrator(headless=headless) as orchestrator:
            offers = orchestrator.scrape_leaflet_offers(shop, leaflet_id)
        
        progress.update(task, completed=True)
    
    console.print(f"\n[bold green]✓ Scraped {len(offers)} offers[/bold green]")
    
    # Show sample offers
    if offers:
        console.print("\n[bold]Sample offers:[/bold]")
        for offer in offers[:5]:
            price_str = f"{offer.price} zł" if offer.price else "N/A"
            console.print(f"  • {offer.name} - {price_str}")


@app.command()
def scrape_full_shop(
    shop: str = typer.Argument(..., help="Shop slug"),
    active_only: bool = typer.Option(
        True,
        "--active-only/--all",
        help="Only scrape active leaflets"
    ),
    headless: bool = typer.Option(False, "--headless")
):
    """Scrape all data for a shop (leaflets, offers, keywords)"""
    console.print(
        f"[bold blue]Scraping all data for {shop}...[/bold blue]"
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scraping...", total=None)
        
        with ScraperOrchestrator(headless=headless) as orchestrator:
            stats = orchestrator.scrape_all_shop_data(shop, active_only)
        
        progress.update(task, completed=True)
    
    # Display statistics
    console.print("\n[bold green]✓ Scraping completed[/bold green]")
    console.print(f"  Leaflets: {stats['leaflets_count']}")
    console.print(f"  Offers: {stats['offers_count']}")
    console.print(f"  Keywords: {stats['keywords_count']}")
    
    if stats['errors']:
        console.print(f"\n[bold red]⚠ Errors: {len(stats['errors'])}[/bold red]")
        for error in stats['errors']:
            console.print(f"  • {error}")


@app.command()
def list_shops():
    """List all scraped shops"""
    storage = JSONStorage(settings.data_dir / "shops", Shop)
    shops_file = settings.data_dir / "shops" / "shops.json"
    
    if not shops_file.exists():
        console.print("[yellow]No shops found. Run 'scrape-shops' first.[/yellow]")
        return
    
    with open(shops_file) as f:
        data = json.load(f)
        shops = [Shop.model_validate(s) for s in data]
    
    table = Table(title="Scraped Shops")
    table.add_column("Slug", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Leaflets", justify="right")
    table.add_column("Popular", justify="center")
    
    for shop in sorted(shops, key=lambda s: s.name):
        table.add_row(
            shop.slug,
            shop.name,
            str(shop.leaflet_count),
            "✓" if shop.is_popular else ""
        )
    
    console.print(table)
    console.print(f"\nTotal: {len(shops)} shops")


@app.command()
def list_leaflets(
    shop: str = typer.Argument(..., help="Shop slug"),
    active_only: bool = typer.Option(
        False,
        "--active-only",
        help="Only show active leaflets"
    )
):
    """List all scraped leaflets for a shop"""
    shop_dir = settings.data_dir / "leaflets" / shop
    
    if not shop_dir.exists():
        console.print(
            f"[yellow]No leaflets found for {shop}. "
            f"Run 'scrape-leaflets {shop}' first.[/yellow]"
        )
        return
    
    storage = JSONStorage(shop_dir, Leaflet)
    leaflets = storage.load_all()
    
    if active_only:
        leaflets = [l for l in leaflets if l.is_active_now()]
    
    table = Table(title=f"Leaflets for {shop}")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Valid Period", style="magenta")
    
    for leaflet in sorted(leaflets, key=lambda l: l.valid_from, reverse=True):
        table.add_row(
            str(leaflet.leaflet_id),
            leaflet.name[:50] + "..." if len(leaflet.name) > 50 else leaflet.name,
            leaflet.status.value,
            f"{leaflet.valid_from.strftime('%Y-%m-%d')} to "
            f"{leaflet.valid_until.strftime('%Y-%m-%d')}"
        )
    
    console.print(table)
    console.print(f"\nTotal: {len(leaflets)} leaflets")


@app.command()
def config():
    """Show current configuration"""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Data Directory", str(settings.data_dir))
    table.add_row("Base URL", settings.base_url)
    table.add_row("Headless", str(settings.headless))
    table.add_row("Request Delay", f"{settings.request_delay_min}-{settings.request_delay_max}s")
    table.add_row("Log Level", settings.log_level)
    table.add_row("Log Format", settings.log_format)
    
    console.print(table)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()