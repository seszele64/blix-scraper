"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
from unittest.mock import Mock
from bs4 import BeautifulSoup


@pytest.fixture
def fixtures_dir() -> Path:
    """Get fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def html_fixtures_dir(fixtures_dir) -> Path:
    """Get HTML fixtures directory."""
    return fixtures_dir / "html"


@pytest.fixture
def shops_html(html_fixtures_dir) -> str:
    """
    Load shops page HTML fixture.
    
    If fixture doesn't exist, returns empty HTML.
    """
    fixture_path = html_fixtures_dir / "shops_page.html"
    
    if fixture_path.exists():
        return fixture_path.read_text(encoding='utf-8')
    
    # Return minimal HTML if fixture not available
    return """
    <html>
        <body>
            <section class="section-n__items--brands">
                <a href="/sklep/biedronka/" title="Biedronka">
                    <div class="brand section-n__item">
                        <img class="brand__logo" src="https://img.blix.pl/brand/23.jpg" />
                    </div>
                </a>
            </section>
        </body>
    </html>
    """


@pytest.fixture
def mock_driver(shops_html):
    """
    Mock Selenium WebDriver.
    
    Returns a mock that provides page_source from fixture.
    """
    driver = Mock()
    driver.page_source = shops_html
    driver.get = Mock()
    driver.quit = Mock()
    driver.execute_script = Mock(return_value=0)
    driver.set_page_load_timeout = Mock()
    
    # Mock capabilities
    driver.capabilities = {'browserVersion': '120.0.0'}
    
    # Mock find_element for wait conditions
    mock_element = Mock()
    driver.find_element = Mock(return_value=mock_element)
    
    return driver


@pytest.fixture
def sample_shop_dict() -> dict:
    """Sample shop data as dictionary."""
    return {
        "slug": "biedronka",
        "brand_id": 23,
        "name": "Biedronka",
        "logo_url": "https://img.blix.pl/image/brand/thumbnail_23.jpg",
        "category": "Sklepy spożywcze",
        "leaflet_count": 13,
        "is_popular": True,
        "scraped_at": "2025-10-30T12:00:00Z"
    }


@pytest.fixture
def sample_leaflet_dict() -> dict:
    """Sample leaflet data as dictionary."""
    return {
        "leaflet_id": 457727,
        "shop_slug": "biedronka",
        "name": "Od środy",
        "cover_image_url": "https://imgproxy.blix.pl/image/leaflet/457727/cover.jpg",
        "url": "https://blix.pl/sklep/biedronka/gazetka/457727/",
        "valid_from": "2025-10-29T00:00:00Z",
        "valid_until": "2025-11-05T23:59:59Z",
        "status": "active",
        "page_count": 12,
        "scraped_at": "2025-10-30T12:05:00Z"
    }