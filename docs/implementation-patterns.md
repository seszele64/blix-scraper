# Implementation Patterns (Revised)

## 1. Selenium WebDriver Setup

### 1.1 Undetected Chrome Configuration

```python
# filepath: /home/tr1x/programming/blix-scraper/src/webdriver/driver_factory.py

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

class DriverFactory:
    """
    Factory for creating undetected Chrome WebDriver instances.
    
    Uses webdriver-manager to auto-handle version matching.
    """
    
    @staticmethod
    def create_driver(
        headless: bool = False,
        user_data_dir: Optional[str] = None,
        window_size: tuple = (1920, 1080)
    ) -> uc.Chrome:
        """
        Create Chrome WebDriver with anti-detection.
        
        Args:
            headless: Run in headless mode (faster, no UI)
            user_data_dir: Path to Chrome profile (for cookies/session)
            window_size: Browser window dimensions
            
        Returns:
            Configured Chrome WebDriver instance
        """
        options = Options()
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
        
        # Optional headless mode
        if headless:
            options.add_argument('--headless=new')  # New headless mode
        
        # Optional persistent profile
        if user_data_dir:
            options.add_argument(f'--user-data-dir={user_data_dir}')
        
        # Create driver
        try:
            logger.info("creating_driver", headless=headless)
            
            driver = uc.Chrome(
                options=options,
                driver_executable_path=ChromeDriverManager().install(),
                version_main=None  # Auto-detect Chrome version
            )
            
            logger.info("driver_created", version=driver.capabilities['browserVersion'])
            return driver
            
        except Exception as e:
            logger.error("driver_creation_failed", error=str(e))
            raise

# Usage example
driver = DriverFactory.create_driver(headless=True)
try:
    driver.get("https://blix.pl/sklepy/")
    # ... scraping logic
finally:
    driver.quit()
```

### 1.2 Selenium Helper Utilities

```python
# filepath: /home/tr1x/programming/blix-scraper/src/webdriver/helpers.py

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import random

def human_delay(min_sec: float = 2.0, max_sec: float = 5.0):
    """
    Random delay to simulate human behavior.
    
    Args:
        min_sec: Minimum delay in seconds
        max_sec: Maximum delay in seconds
    """
    time.sleep(random.uniform(min_sec, max_sec))

def wait_for_element(
    driver, 
    by: By, 
    value: str, 
    timeout: int = 10
):
    """
    Wait for element to be present in DOM.
    
    Args:
        driver: Selenium WebDriver instance
        by: Locator strategy (By.CSS_SELECTOR, etc.)
        value: Selector value
        timeout: Max wait time in seconds
        
    Returns:
        WebElement if found
        
    Raises:
        TimeoutException if not found
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        raise TimeoutException(f"Element not found: {by}={value}")

def scroll_to_bottom(driver, pause_time: float = 1.0):
    """
    Scroll to bottom of page to trigger lazy loading.
    
    Args:
        driver: Selenium WebDriver instance
        pause_time: Pause between scrolls (seconds)
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        
        # Calculate new height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        
        last_height = new_height
```

---

## 2. Scraper Pattern with Selenium

### 2.1 Base Scraper

```python
# filepath: /home/tr1x/programming/blix-scraper/src/scrapers/base.py

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
import structlog

from ..webdriver.helpers import human_delay

T = TypeVar('T')

class BaseScraper(ABC, Generic[T]):
    """
    Abstract base scraper using Selenium + BeautifulSoup.
    
    Template Method pattern for scraping workflow.
    """
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._logger = structlog.get_logger(self.__class__.__name__)
    
    def scrape(self, url: str) -> List[T]:
        """
        Template method for scraping workflow.
        
        Steps:
        1. Navigate to URL
        2. Wait for page load
        3. Get page source
        4. Parse HTML
        5. Extract entities
        6. Validate
        """
        self._logger.info("scrape_started", url=url)
        
        try:
            # Navigate
            self.driver.get(url)
            human_delay()  # Anti-detection
            
            # Wait for content
            self._wait_for_content()
            
            # Get HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract entities
            entities = self._extract_entities(soup, url)
            validated = self._validate_entities(entities)
            
            self._logger.info("scrape_completed", url=url, count=len(validated))
            return validated
            
        except Exception as e:
            self._logger.error("scrape_failed", url=url, error=str(e), exc_info=True)
            raise
    
    @abstractmethod
    def _wait_for_content(self):
        """Wait for page-specific content to load."""
        pass
    
    @abstractmethod
    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[T]:
        """Extract domain entities from parsed HTML."""
        pass
    
    def _validate_entities(self, entities: List[T]) -> List[T]:
        """Validate entities (default: pass-through)."""
        return entities
```

### 2.2 Concrete Shop Scraper

```python
# filepath: /home/tr1x/programming/blix-scraper/src/scrapers/shop_scraper.py

from typing import List
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from datetime import datetime

from .base import BaseScraper
from ..domain.entities import Shop
from ..webdriver.helpers import wait_for_element

class ShopScraper(BaseScraper[Shop]):
    """
    Scraper for shop/brand listings.
    
    Extracts shops from https://blix.pl/sklepy/
    """
    
    def _wait_for_content(self):
        """Wait for brand items to load."""
        wait_for_element(
            self.driver,
            By.CSS_SELECTOR,
            '.section-n__items--brands',
            timeout=10
        )
    
    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[Shop]:
        """Extract Shop entities from HTML."""
        shops = []
        
        # Find all brand containers
        containers = soup.select('.section-n__items--brands')
        
        for container in containers:
            # Determine if this is "popular shops" section
            section = container.find_parent('section')
            is_popular = False
            if section:
                heading = section.select_one('h2')
                if heading and 'Popularne sklepy' in heading.text:
                    is_popular = True
            
            # Extract each brand
            for brand_div in container.select('.brand.section-n__item'):
                try:
                    shop = self._extract_shop(brand_div, is_popular)
                    if shop:
                        shops.append(shop)
                except Exception as e:
                    self._logger.warning(
                        "shop_extraction_error",
                        error=str(e),
                        html=str(brand_div)[:200]
                    )
                    continue
        
        return shops
    
    def _extract_shop(self, brand_div, is_popular: bool) -> Shop:
        """Extract single shop from brand div."""
        # Get parent link
        link = brand_div.find_parent('a')
        if not link:
            return None
        
        href = link.get('href', '')
        slug = href.strip('/').split('/')[-1]
        
        # Extract elements
        name_elem = brand_div.select_one('.brand__name')
        logo_elem = brand_div.select_one('.brand__logo')
        count_elem = brand_div.select_one('.brand__count')
        
        if not all([name_elem, logo_elem, slug]):
            self._logger.warning("incomplete_shop_data", slug=slug)
            return None
        
        # Parse leaflet count (e.g., "13 gazetek" -> 13)
        leaflet_count = 0
        if count_elem:
            count_text = count_elem.text.strip().split()[0]
            try:
                leaflet_count = int(count_text)
            except ValueError:
                pass
        
        # Create Shop entity
        return Shop(
            slug=slug,
            brand_id=None,  # Not available in this view
            name=name_elem.text.strip(),
            logo_url=logo_elem.get('data-src') or logo_elem.get('src'),
            category=None,  # Determine from context if needed
            leaflet_count=leaflet_count,
            is_popular=is_popular,
            scraped_at=datetime.utcnow()
        )
```

---

## 3. Testing with Realistic HTML Fixtures

### 3.1 Fixture Structure

```
tests/
├── fixtures/
│   ├── html/
│   │   ├── shops_page.html         # Full /sklepy/ page
│   │   ├── biedronka_shop.html     # /sklep/biedronka/
│   │   ├── leaflet_457727.html     # Individual leaflet page
│   │   └── offers_fragment.html    # Offer elements only
│   └── json/
│       ├── expected_shops.json     # Expected parsed output
│       └── expected_leaflets.json
```

### 3.2 Capturing Real HTML

```python
# filepath: /home/tr1x/programming/blix-scraper/tests/utils/capture_html.py

"""
Utility to capture real HTML from blix.pl for testing.

Usage:
    python -m tests.utils.capture_html --url https://blix.pl/sklepy/ --output tests/fixtures/html/shops_page.html
"""

import argparse
from pathlib import Path
from src.webdriver.driver_factory import DriverFactory
from src.webdriver.helpers import human_delay

def capture_html(url: str, output_path: Path):
    """
    Capture HTML from URL and save to file.
    
    Args:
        url: Target URL
        output_path: Where to save HTML
    """
    driver = DriverFactory.create_driver(headless=True)
    
    try:
        print(f"Fetching {url}...")
        driver.get(url)
        human_delay(3, 5)  # Wait for full page load
        
        html = driver.page_source
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        
        print(f"HTML saved to {output_path}")
        print(f"Size: {len(html)} characters")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    
    capture_html(args.url, args.output)
```

### 3.3 Test with Real HTML Fixture

```python
# filepath: /home/tr1x/programming/blix-scraper/tests/scrapers/test_shop_scraper.py

import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from src.scrapers.shop_scraper import ShopScraper
from src.domain.entities import Shop

@pytest.fixture
def shops_html():
    """Load real HTML fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures/html/shops_page.html"
    return fixture_path.read_text(encoding='utf-8')

@pytest.fixture
def mock_driver(shops_html):
    """Mock Selenium driver that returns fixture HTML."""
    class MockDriver:
        page_source = shops_html
        
        def get(self, url):
            pass
        
        def find_element(self, by, value):
            # Return mock element for wait conditions
            return type('Element', (), {})()
    
    return MockDriver()

def test_extract_shops_from_real_html(mock_driver, shops_html):
    """Test parsing shops from actual blix.pl HTML."""
    scraper = ShopScraper(mock_driver)
    soup = BeautifulSoup(shops_html, 'lxml')
    
    shops = scraper._extract_entities(soup, "https://blix.pl/sklepy/")
    
    # Assertions based on real data
    assert len(shops) > 0
    assert any(s.slug == "biedronka" for s in shops)
    
    biedronka = next(s for s in shops if s.slug == "biedronka")
    assert biedronka.name == "Biedronka"
    assert biedronka.leaflet_count > 0
    assert "blix.pl" in str(biedronka.logo_url)

def test_extract_popular_shops(mock_driver, shops_html):
    """Test identifying popular shops."""
    scraper = ShopScraper(mock_driver)
    soup = BeautifulSoup(shops_html, 'lxml')
    
    shops = scraper._extract_entities(soup, "https://blix.pl/sklepy/")
    popular_shops = [s for s in shops if s.is_popular]
    
    assert len(popular_shops) > 0
    assert any(s.slug == "biedronka" for s in popular_shops)
```

---

## 4. Configuration

```python
# filepath: /home/tr1x/programming/blix-scraper/src/config.py

from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application configuration."""
    
    # Paths
    data_dir: Path = Path("data")
    cache_dir: Path = Path("data/cache")
    
    # WebDriver
    headless: bool = False
    chrome_profile_dir: str | None = None
    window_size: tuple[int, int] = (1920, 1080)
    
    # Scraping
    request_delay_min: float = 2.0
    request_delay_max: float = 5.0
    max_retries: int = 3
    retry_backoff: float = 2.0
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "console"  # or "json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

This revised architecture is much more practical and focused on your actual needs!