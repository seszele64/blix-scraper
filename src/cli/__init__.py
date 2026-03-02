"""CLI interface for Blix scraper."""

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import structlog
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..config import settings
from ..domain.date_filter import DateFilterOptions
from ..domain.entities import Leaflet, Offer, SearchResult, Shop
from ..logging_config import setup_logging
from ..services import ScraperService

if TYPE_CHECKING:
    from datetime import datetime

# Setup logging
setup_logging()

logger = structlog.get_logger(__name__)

# Create Typer app
app = typer.Typer(name="blix-scraper", help="Web scraper for blix.pl promotional leaflets")

console = Console()


def _parse_date(date_str: str | None) -> "datetime | None":
    """Parse date string to datetime.

    Args:
        date_str: Date string to parse (supports: YYYY-MM-DD, 'today', relative dates)

    Returns:
        Parsed datetime or None if input is None
    """
    if date_str is None:
        return None

    # Handle relative dates
    date_str_lower = date_str.lower().strip()

    if date_str_lower == "today":
        return datetime.now(timezone.utc)

    if date_str_lower == "tomorrow":
        return datetime.now(timezone.utc) + timedelta(days=1)

    # Handle "this weekend" (Saturday)
    if date_str_lower == "this weekend":
        now = datetime.now(timezone.utc)
        days_until_saturday = (5 - now.weekday()) % 7
        if days_until_saturday == 0 and now.weekday() == 5:
            # Already Saturday, get next Saturday
            days_until_saturday = 7
        return now + timedelta(days=days_until_saturday)

    # Handle "next week" (Monday of next week)
    if date_str_lower == "next week":
        now = datetime.now(timezone.utc)
        days_until_monday = (7 - now.weekday()) % 7 + 1
        return now + timedelta(days=days_until_monday)

    # Handle "end of month"
    if date_str_lower == "end of month":
        from calendar import monthrange

        now = datetime.now(timezone.utc)
        _, last_day = monthrange(now.year, now.month)
        return now.replace(day=last_day, hour=23, minute=59, second=59)

    # Try parsing as date
    try:
        # Try parsing date with time
        return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    # Try parsing just date
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    # Return None if parsing fails, will be handled later
    console.print(f"[yellow]Warning: Could not parse date '{date_str}'[/yellow]")
    return None


def _build_date_filter(
    active_on: str | None,
    valid_from: str | None,
    valid_until: str | None,
    within_range: str | None,
) -> DateFilterOptions | None:
    """Build DateFilterOptions from CLI arguments.

    Args:
        active_on: Date string for active_on filter
        valid_from: Date string for valid_from filter
        valid_until: Date string for valid_until filter
        within_range: Date range string (e.g., '2024-01-01 to 2024-01-31')

    Returns:
        DateFilterOptions or None if no filters provided
    """
    date_from: datetime | None = None
    date_to: datetime | None = None

    # Parse within_range first
    if within_range:
        parts = within_range.split(" to ")
        if len(parts) == 2:
            date_from = _parse_date(parts[0].strip())
            date_to = _parse_date(parts[1].strip())
        else:
            console.print(
                "[yellow]Warning: Invalid range format. Use 'YYYY-MM-DD to YYYY-MM-DD'[/yellow]"
            )

    # Parse individual date filters
    parsed_active_on = _parse_date(active_on)
    parsed_valid_from = _parse_date(valid_from)
    parsed_valid_until = _parse_date(valid_until)

    # Use parsed values if not set from within_range
    if date_from is None and parsed_valid_from:
        date_from = parsed_valid_from
    if date_to is None and parsed_valid_until:
        date_to = parsed_valid_until

    # Build filter options
    filter_options = DateFilterOptions(
        active_on=parsed_active_on,
        valid_from=parsed_valid_from if parsed_valid_from and not within_range else None,
        valid_until=parsed_valid_until if parsed_valid_until and not within_range else None,
        date_from=date_from,
        date_to=date_to,
    )

    return filter_options if filter_options.has_date_filter() else None


def _display_shops_table(shops: list[Shop]) -> None:
    """Display shops in a Rich table.

    Args:
        shops: List of Shop entities
    """
    table = Table(title="Shops")
    table.add_column("Slug", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Leaflets", justify="right")
    table.add_column("Popular", justify="center")
    table.add_column("Category", style="dim")

    for shop in sorted(shops, key=lambda s: s.name):
        table.add_row(
            shop.slug,
            shop.name,
            str(shop.leaflet_count),
            "✓" if shop.is_popular else "",
            shop.category or "",
        )

    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {len(shops)} shops")


def _display_leaflets_table(leaflets: list[Leaflet], shop_slug: str) -> None:
    """Display leaflets in a Rich table.

    Args:
        leaflets: List of Leaflet entities
        shop_slug: Shop slug for context
    """
    table = Table(title=f"Leaflets for {shop_slug}")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Valid From", style="yellow")
    table.add_column("Valid Until", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Pages", justify="right")

    for leaflet_sorted in sorted(leaflets, key=lambda leaf: leaf.valid_from, reverse=True):
        table.add_row(
            str(leaflet_sorted.leaflet_id),
            leaflet_sorted.name,
            leaflet_sorted.valid_from.strftime("%Y-%m-%d") if leaflet_sorted.valid_from else "N/A",
            leaflet_sorted.valid_until.strftime("%Y-%m-%d")
            if leaflet_sorted.valid_until
            else "N/A",
            leaflet_sorted.status.value,
            str(leaflet_sorted.page_count) if leaflet_sorted.page_count else "N/A",
        )

    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {len(leaflets)} leaflets")


def _display_offers_table(offers: list[Offer], limit: int = 20) -> None:
    """Display offers in a Rich table.

    Args:
        offers: List of Offer entities
        limit: Maximum number of offers to display
    """
    display_offers = offers[:limit]

    table = Table(title=f"Offers (showing {len(display_offers)} of {len(offers)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Price", style="yellow", justify="right")
    table.add_column("Page", justify="right")
    table.add_column("Valid", style="dim")

    for offer in display_offers:
        price_str = f"{offer.price:.2f} PLN" if offer.price else "N/A"
        valid_str = f"{offer.valid_from.strftime('%m/%d')} - {offer.valid_until.strftime('%m/%d')}"

        table.add_row(
            str(offer.leaflet_id),
            offer.name[:50] + "..." if len(offer.name) > 50 else offer.name,
            price_str,
            str(offer.page_number),
            valid_str,
        )

    console.print(table)

    if len(offers) > limit:
        console.print(
            f"\n[dim]Showing {limit} of {len(offers)} offers. Use --all to show all.[/dim]"
        )


def _display_search_results_table(results: list[SearchResult], limit: int = 20) -> None:
    """Display search results in a Rich table.

    Args:
        results: List of SearchResult entities
        limit: Maximum number of results to display
    """
    display_results = results[:limit]

    table = Table(title=f"Search Results (showing {len(display_results)} of {len(results)})")
    table.add_column("Name", style="green")
    table.add_column("Price", style="yellow", justify="right")
    table.add_column("Shop", style="cyan")
    table.add_column("Discount", style="magenta", justify="right")
    table.add_column("Valid", style="dim")

    for result in display_results:
        price_str = f"{result.price_pln:.2f} PLN" if result.price_pln else "N/A"
        discount_str = f"-{result.percent_discount}%" if result.percent_discount > 0 else ""
        shop_str = result.shop_name or "N/A"
        valid_str = (
            f"{result.valid_from.strftime('%m/%d')} - {result.valid_until.strftime('%m/%d')}"
        )

        table.add_row(
            result.name[:50] + "..." if len(result.name) > 50 else result.name,
            price_str,
            shop_str,
            discount_str,
            valid_str,
        )

    console.print(table)

    if len(results) > limit:
        console.print(
            f"\n[dim]Showing {limit} of {len(results)} results. Use --all to show all.[/dim]"
        )


@app.command()
def scrape_shops(
    headless: bool = typer.Option(False, "--headless", help="Run browser in headless mode"),
) -> None:
    """Scrape all shops from blix.pl/sklepy/"""
    try:
        with ScraperService(headless=headless) as service:
            console.print("[bold blue]Fetching shops...[/bold blue]")
            shops = service.get_shops()
            _display_shops_table(shops)

    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("scrape_shops_failed", error=str(e))
        console.print(f"[bold red]Failed to scrape shops:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query (e.g., 'kawa')"),
    headless: bool = typer.Option(False, "--headless"),
    show_all: bool = typer.Option(False, "--all", help="Show all results (default: limit to 20)"),
    no_filter: bool = typer.Option(
        False,
        "--no-filter",
        help="Don't filter by product name (show all offers from matching leaflets)",
    ),
    active_on: str | None = typer.Option(
        None,
        "--active-on",
        "-a",
        help="Search in leaflets active on specific date "
        "(e.g., '2024-01-20', 'today', 'this weekend')",
    ),
    valid_from: str | None = typer.Option(
        None,
        "--valid-from",
        "-f",
        help="Search in leaflets valid from date (e.g., '2024-01-01', 'next week')",
    ),
    valid_until: str | None = typer.Option(
        None,
        "--valid-until",
        "-u",
        help="Search in leaflets valid until date (e.g., '2024-01-31', 'end of month')",
    ),
    within_range: str | None = typer.Option(
        None,
        "--within-range",
        "-r",
        help="Search in leaflets within date range (e.g., '2024-01-01 to 2024-01-31')",
    ),
) -> None:
    """Search for products across all shops"""
    try:
        # Build date filter
        date_filter = _build_date_filter(active_on, valid_from, valid_until, within_range)

        if date_filter:
            console.print("[dim]Date filter active[/dim]")

        with ScraperService(headless=headless) as service:
            console.print(f"[bold blue]Searching for '{query}'...[/bold blue]")
            results = service.search(
                query=query,
                filter_by_name=not no_filter,
                date_filter=date_filter,
            )

            limit = 1000 if show_all else 20
            _display_search_results_table(results, limit=limit)

    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("search_failed", query=query, error=str(e))
        console.print(f"[bold red]Search failed:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def scrape_leaflets(
    shop: str = typer.Argument(..., help="Shop slug (e.g., 'biedronka')"),
    headless: bool = typer.Option(False, "--headless"),
    active_on: str | None = typer.Option(
        None,
        "--active-on",
        "-a",
        help="Show leaflets active on specific date (e.g., '2024-01-20', 'today', 'this weekend')",
    ),
    valid_from: str | None = typer.Option(
        None,
        "--valid-from",
        "-f",
        help="Show leaflets valid from date (e.g., '2024-01-01', 'next week')",
    ),
    valid_until: str | None = typer.Option(
        None,
        "--valid-until",
        "-u",
        help="Show leaflets valid until date (e.g., '2024-01-31', 'end of month')",
    ),
    within_range: str | None = typer.Option(
        None,
        "--within-range",
        "-r",
        help="Show leaflets within date range (e.g., '2024-01-01 to 2024-01-31')",
    ),
) -> None:
    """Scrape all leaflets for a specific shop"""
    try:
        # Build date filter
        date_filter = _build_date_filter(active_on, valid_from, valid_until, within_range)

        if date_filter:
            console.print("[dim]Date filter active[/dim]")

        with ScraperService(headless=headless) as service:
            console.print(f"[bold blue]Fetching leaflets for '{shop}'...[/bold blue]")
            leaflets = service.get_leaflets(shop, date_filter=date_filter)
            _display_leaflets_table(leaflets, shop)

    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("scrape_leaflets_failed", shop=shop, error=str(e))
        console.print(f"[bold red]Failed to scrape leaflets:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def scrape_offers(
    shop: str = typer.Argument(..., help="Shop slug"),
    leaflet_id: int = typer.Argument(..., help="Leaflet ID"),
    headless: bool = typer.Option(False, "--headless"),
    show_all: bool = typer.Option(False, "--all", help="Show all offers"),
) -> None:
    """Scrape offers for a specific leaflet"""
    try:
        with ScraperService(headless=headless) as service:
            console.print(f"[bold blue]Fetching leaflets to find ID {leaflet_id}...[/bold blue]")

            # First get the leaflets to find the specific one
            leaflets = service.get_leaflets(shop)

            # Find the matching leaflet
            leaflet: Leaflet | None = None
            for leaf in leaflets:
                if leaf.leaflet_id == leaflet_id:
                    leaflet = leaf
                    break

            if leaflet is None:
                console.print(f"[bold red]Leaflet with ID {leaflet_id} not found[/bold red]")
                raise typer.Exit(1)

            console.print(f"[bold blue]Fetching offers from '{leaflet.name}'...[/bold blue]")
            offers = service.get_offers(shop, leaflet)

            limit = 1000 if show_all else 20
            _display_offers_table(offers, limit=limit)

    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("scrape_offers_failed", shop=shop, leaflet_id=leaflet_id, error=str(e))
        console.print(f"[bold red]Failed to scrape offers:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def scrape_full_shop(
    shop: str = typer.Argument(..., help="Shop slug"),
    active_only: bool = typer.Option(
        True, "--active-only/--all", help="Only scrape active leaflets"
    ),
    headless: bool = typer.Option(False, "--headless"),
) -> None:
    """Scrape all data for a shop (leaflets, offers, keywords)"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            with ScraperService(headless=headless) as service:
                # Step 1: Get shop info
                task1 = progress.add_task("[cyan]Fetching shops...", total=None)
                shops = service.get_shops()
                shop_obj = next((s for s in shops if s.slug == shop), None)

                if shop_obj is None:
                    console.print(f"[bold red]Shop '{shop}' not found[/bold red]")
                    raise typer.Exit(1)

                progress.update(task1, completed=True)
                console.print(f"[green]Found shop: {shop_obj.name}[/green]")

                # Step 2: Get leaflets
                task2 = progress.add_task("[cyan]Fetching leaflets...", total=None)
                leaflets = service.get_leaflets(shop)

                if active_only:
                    leaflets = [leaf for leaf in leaflets if leaf.status.value == "active"]

                progress.update(task2, completed=True)
                console.print(f"[green]Found {len(leaflets)} leaflets[/green]")

                # Step 3: Get offers for each leaflet
                total_offers = 0
                total_keywords = 0

                task3 = progress.add_task(
                    f"[cyan]Fetching offers and keywords ({len(leaflets)} leaflets)...",
                    total=len(leaflets),
                )

                for leaflet in leaflets:
                    try:
                        offers = service.get_offers(shop, leaflet)
                        total_offers += len(offers)

                        keywords = service.get_keywords(shop, leaflet)
                        total_keywords += len(keywords)
                    except Exception as e:
                        logger.warning(
                            "failed_to_fetch_leaflet_data",
                            leaflet_id=leaflet.leaflet_id,
                            error=str(e),
                        )

                    progress.advance(task3)

                progress.update(task3, completed=True)

                # Display summary
                console.print("\n[bold green]Scraping Complete![/bold green]")
                table = Table(title="Scrape Summary")
                table.add_column("Metric", style="cyan")
                table.add_column("Count", style="yellow", justify="right")

                table.add_row("Leaflets", str(len(leaflets)))
                table.add_row("Offers", str(total_offers))
                table.add_row("Keywords", str(total_keywords))

                console.print(table)

    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("scrape_full_shop_failed", shop=shop, error=str(e))
        console.print(f"[bold red]Failed to scrape shop:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def config() -> None:
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


def main() -> None:
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
