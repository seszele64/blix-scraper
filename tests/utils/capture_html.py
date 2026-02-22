r"""
Utility to capture real HTML from blix.pl for testing.

Usage:
    python -m tests.utils.capture_html \
        --url https://blix.pl/sklepy/ \
        --output tests/fixtures/html/shops_page.html
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.logging_config import setup_logging
from src.webdriver.driver_factory import DriverFactory
from src.webdriver.helpers import human_delay


def capture_html(url: str, output_path: Path) -> None:
    """
    Capture HTML from URL and save to file.

    Args:
        url: Target URL
        output_path: Where to save HTML
    """
    print(f"Fetching {url}...")

    driver = DriverFactory.create_driver(headless=True)

    try:
        driver.get(url)
        human_delay(3, 5)  # Wait for full page load

        html = driver.page_source

        # Create directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        print(f"✓ HTML saved to {output_path}")
        print(f"  Size: {len(html):,} characters")
        print(f"  Lines: {html.count(chr(10)):,}")

    finally:
        driver.quit()


def main() -> None:
    """Main entry point."""
    setup_logging()

    parser = argparse.ArgumentParser(description="Capture HTML from blix.pl for testing")
    parser.add_argument("--url", required=True, help="Target URL to capture")
    parser.add_argument("--output", required=True, type=Path, help="Output file path")

    args = parser.parse_args()

    try:
        capture_html(args.url, args.output)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
