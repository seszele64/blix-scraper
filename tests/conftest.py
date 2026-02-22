"""Pytest configuration and shared fixtures."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.config import Settings


@pytest.fixture
def fixtures_dir() -> Path:
    """Get fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def html_fixtures_dir(fixtures_dir) -> Path:
    """Get HTML fixtures directory."""
    return fixtures_dir / "html"


@pytest.fixture(scope="session")
def test_config(tmp_path_factory) -> Settings:
    """
    Create test-specific configuration.

    Returns a Settings instance configured for testing with temporary
    directories and test-specific settings.

    Yields:
        Settings: Test configuration instance.
    """
    # Create temporary directories for test data
    tmp_dir = tmp_path_factory.mktemp("test_data")
    test_data_dir = tmp_dir / "data"
    test_cache_dir = tmp_dir / "cache"

    test_data_dir.mkdir(parents=True, exist_ok=True)
    test_cache_dir.mkdir(parents=True, exist_ok=True)

    # Create test configuration
    config = Settings(
        data_dir=test_data_dir,
        cache_dir=test_cache_dir,
        headless=True,
        window_width=1280,
        window_height=720,
        request_delay_min=0.1,
        request_delay_max=0.2,
        max_retries=1,
        retry_backoff=0.5,
        page_load_timeout=10,
        log_level="DEBUG",
        log_format="console",
        base_url="https://test.blix.pl",
        shops_url="https://test.blix.pl/sklepy/",
    )

    return config


@pytest.fixture
def shops_html(html_fixtures_dir) -> str:
    """
    Load shops page HTML fixture.

    If fixture doesn't exist, returns empty HTML.
    """
    fixture_path = html_fixtures_dir / "shops_page.html"

    if fixture_path.exists():
        return fixture_path.read_text(encoding="utf-8")

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
    Mock Selenium WebDriver with comprehensive mocking.

    Returns a mock that provides page_source from fixture and supports
    common Selenium operations like find_element, find_elements,
    switch_to, execute_script, and more.

    Yields:
        Mock: Configured mock WebDriver instance.
    """
    driver = Mock()
    driver.page_source = shops_html
    driver.get = Mock()
    driver.quit = Mock()
    driver.execute_script = Mock(return_value=0)
    driver.set_page_load_timeout = Mock()
    driver.implicitly_wait = Mock()

    # Mock capabilities
    driver.capabilities = {"browserVersion": "120.0.0", "browserName": "chrome"}

    # Mock current_url
    driver.current_url = "https://test.blix.pl/sklepy/"

    # Mock title
    driver.title = "Test Page"

    # Mock window handling
    driver.current_window_handle = "window-1"
    driver.window_handles = ["window-1"]

    # Mock find_element
    mock_element = Mock()
    mock_element.text = "Test Element"
    mock_element.get_attribute = Mock(return_value="test-value")
    mock_element.is_displayed = Mock(return_value=True)
    mock_element.is_enabled = Mock(return_value=True)
    driver.find_element = Mock(return_value=mock_element)

    # Mock find_elements
    driver.find_elements = Mock(return_value=[mock_element])

    # Mock switch_to
    mock_switch_to = Mock()
    mock_frame = Mock()
    mock_window = Mock()
    mock_alert = Mock()
    mock_alert.text = "Test Alert"
    mock_alert.accept = Mock()
    mock_alert.dismiss = Mock()
    mock_switch_to.frame = mock_frame
    mock_switch_to.window = mock_window
    mock_switch_to.alert = mock_alert
    mock_switch_to.default_content = Mock()
    driver.switch_to = mock_switch_to

    # Mock cookies
    driver.get_cookies = Mock(
        return_value=[{"name": "test_cookie", "value": "test_value", "domain": ".test.blix.pl"}]
    )
    driver.add_cookie = Mock()
    driver.delete_cookie = Mock()
    driver.delete_all_cookies = Mock()

    # Mock navigation
    driver.back = Mock()
    driver.forward = Mock()
    driver.refresh = Mock()

    # Mock options
    mock_options = Mock()
    mock_options.add_argument = Mock()
    driver.options = mock_options

    return driver


@pytest.fixture
def mock_wait():
    """
    Mock WebDriverWait and expected_conditions.

    Returns a tuple of (mock_wait, mock_ec) where:
    - mock_wait: Mocked WebDriverWait instance
    - mock_ec: Mocked expected_conditions module

    Yields:
        tuple: (mock_wait, mock_ec)
    """
    # Mock WebDriverWait
    wait = Mock()

    # Mock expected_conditions
    ec = Mock()

    # Common expected conditions
    ec.presence_of_element_located = Mock(
        return_value=lambda driver: driver.find_element("css", "test")
    )
    ec.visibility_of_element_located = Mock(
        return_value=lambda driver: driver.find_element("css", "test")
    )
    ec.element_to_be_clickable = Mock(
        return_value=lambda driver: driver.find_element("css", "test")
    )
    ec.presence_of_all_elements_located = Mock(
        return_value=lambda driver: driver.find_elements("css", "test")
    )
    ec.visibility_of = Mock(return_value=lambda element: element)
    ec.invisibility_of_element_located = Mock(return_value=lambda driver: None)
    ec.title_contains = Mock(return_value=lambda driver: True)
    ec.url_contains = Mock(return_value=lambda driver: True)
    ec.url_to_be = Mock(return_value=lambda driver: True)
    ec.frame_to_be_available_and_switch_to_it = Mock(
        return_value=lambda driver: driver.switch_to.frame
    )

    # Configure wait.until to return a mock element
    mock_element = Mock()
    mock_element.text = "Waited Element"
    mock_element.get_attribute = Mock(return_value="waited-value")
    mock_element.is_displayed = Mock(return_value=True)
    wait.until = Mock(return_value=mock_element)

    return wait, ec


@pytest.fixture
def leaflet_html(html_fixtures_dir) -> str:
    """
    Load leaflet page HTML fixture.

    If fixture doesn't exist, returns empty HTML.
    """
    fixture_path = html_fixtures_dir / "leaflet_page.html"

    if fixture_path.exists():
        return fixture_path.read_text(encoding="utf-8")

    # Return minimal HTML if fixture not available
    return """
    <html>
        <body>
            <div class="leaflet-list">
                <article class="leaflet-item" data-leaflet-id="457727">
                    <a href="/sklep/biedronka/gazetka/457727/">
                        <h3>Od środy</h3>
                    </a>
                </article>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def offer_html(html_fixtures_dir) -> str:
    """
    Load offer page HTML fixture.

    If fixture doesn't exist, returns empty HTML.
    """
    fixture_path = html_fixtures_dir / "offer_page.html"

    if fixture_path.exists():
        return fixture_path.read_text(encoding="utf-8")

    # Return minimal HTML if fixture not available
    return """
    <html>
        <body>
            <div class="offers-container">
                <article class="offer-item" data-offer-id="123456">
                    <h3>Chleb żytni 500g</h3>
                    <div class="offer-item__price">
                        <span class="offer-item__price-value">4,99</span>
                        <span class="offer-item__price-currency">zł</span>
                    </div>
                </article>
            </div>
        </body>
    </html>
    """


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
        "scraped_at": "2025-10-30T12:00:00Z",
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
        "scraped_at": "2025-10-30T12:05:00Z",
    }
