"""
Debug script to inspect search page structure.

This script is useful for:
- Understanding how the search page is structured
- Finding where product data is located
- Debugging scraping issues
- Inspecting HTML elements

Usage:
    python examples/08_debug_search.py <query>

Example:
    python examples/08_debug_search.py kawa
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.webdriver.driver_factory import DriverFactory
from src.webdriver.helpers import human_delay
from src.config import settings
from rich.console import Console
import re
import json

console = Console()


def debug_search_page(query: str):
    """
    Debug the search page to understand its structure.

    This function demonstrates:
    - Navigating to a search URL
    - Analyzing page content
    - Finding data in HTML/JavaScript
    - Saving page source for inspection

    Args:
        query: The search query
    """
    console.print(f"\n[bold cyan]Debugging search for: {query}[/bold cyan]\n")

    url = f"{settings.base_url}/szukaj/?szukaj={query}"
    console.print(f"URL: {url}\n")

    # Create driver (headless=False for manual inspection)
    driver = DriverFactory.create_driver(headless=False)

    try:
        console.print("Loading page...")
        driver.get(url)
        human_delay(5, 7)  # Wait for page to fully load

        # Get page source
        page_source = driver.page_source

        console.print("[bold]Page Analysis:[/bold]\n")
        console.print(f"Page length: {len(page_source)} characters")

        # Look for script tags
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', page_source, re.DOTALL)
        console.print(f"Script tags found: {len(scripts)}\n")

        # Search for 'products' in scripts
        console.print("[bold]Searching for 'products' in scripts:[/bold]\n")

        found_products = False
        for i, script in enumerate(scripts):
            if 'product' in script.lower():
                found_products = True
                console.print(f"[yellow]Script {i+1} contains 'product':[/yellow]")

                # Show snippet
                snippet = script[:500] if len(script) > 500 else script
                console.print(f"{snippet}...\n")

                # Try to find JSON arrays
                json_arrays = re.findall(r'\[[\s\S]{10,1000}\]', script)
                if json_arrays:
                    console.print(f"  Found {len(json_arrays)} potential JSON arrays")

                    for j, arr in enumerate(json_arrays[:3]):  # Show first 3
                        try:
                            data = json.loads(arr)
                            if isinstance(data, list) and len(data) > 0:
                                console.print(f"  [green]Array {j+1}: {len(data)} items[/green]")
                                if isinstance(data[0], dict):
                                    console.print(f"  First item keys: {list(data[0].keys())[:10]}")
                        except Exception:
                            pass

                console.print()

        if not found_products:
            console.print("[yellow]No 'product' keyword found in scripts[/yellow]\n")

        # Check for data attributes
        console.print("[bold]Checking for data attributes:[/bold]\n")
        data_attrs = re.findall(r'data-[a-z-]+=', page_source.lower())
        if data_attrs:
            unique_attrs = set(data_attrs)
            console.print(f"Found data attributes: {', '.join(list(unique_attrs)[:20])}\n")
        else:
            console.print("No data attributes found\n")

        # Check for specific containers
        console.print("[bold]Checking for result containers:[/bold]\n")
        containers = [
            'search-results',
            'product-list',
            'offer-list',
            'results-container',
            'products-container'
        ]

        found_containers = []
        for container in containers:
            if container in page_source.lower():
                found_containers.append(container)
                console.print(f"[green]✓ Found: {container}[/green]")

        if not found_containers:
            console.print("[yellow]No standard container classes found[/yellow]\n")

        # Save full source for inspection
        output_file = Path("debug_search_source.html")
        output_file.write_text(page_source, encoding='utf-8')
        console.print(f"\n[green]✓ Full page source saved to: {output_file}[/green]")
        console.print(f"  File size: {len(page_source)} characters")

        # Keep browser open for manual inspection (if in interactive mode)
        console.print("\n[yellow]Browser window left open for manual inspection.[/yellow]")
        try:
            console.print("Press Enter to close...")
            input()
        except (EOFError, OSError):
            # Non-interactive mode - browser will be closed by finally block
            console.print("[cyan]Non-interactive mode detected. Closing browser...[/cyan]")

    except Exception as e:
        console.print(f"[red]Error during debugging: {e}[/red]")
        raise

    finally:
        if driver:
            driver.quit()
            console.print("\nBrowser closed.")


def main():
    """Main entry point for debug script."""
    if len(sys.argv) < 2:
        console.print("[bold cyan]Blix Scraper - Search Page Debugger[/bold cyan]\n")
        console.print("Usage: python examples/08_debug_search.py <query>\n")
        console.print("Example: python examples/08_debug_search.py kawa\n")
        console.print("This script will:")
        console.print("  1. Open a browser to the search page")
        console.print("  2. Analyze the page structure")
        console.print("  3. Save the page source for inspection")
        console.print("  4. Leave the browser open for manual debugging")
        return

    query = sys.argv[1]
    debug_search_page(query)


if __name__ == "__main__":
    main()
