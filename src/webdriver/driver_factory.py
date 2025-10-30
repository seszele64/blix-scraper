"""WebDriver factory for creating Chrome instances."""

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional
import structlog

from ..config import settings

logger = structlog.get_logger(__name__)


class DriverFactory:
    """Factory for creating undetected Chrome WebDriver instances."""
    
    @staticmethod
    def create_driver(
        headless: Optional[bool] = None,
        user_data_dir: Optional[str] = None,
        window_size: Optional[tuple[int, int]] = None
    ) -> uc.Chrome:
        """
        Create Chrome WebDriver with anti-detection.
        
        Args:
            headless: Run in headless mode (None = use settings)
            user_data_dir: Path to Chrome profile (None = use settings)
            window_size: Browser window dimensions (None = use settings)
            
        Returns:
            Configured Chrome WebDriver instance
        """
        # Use settings defaults if not specified
        if headless is None:
            headless = settings.headless
        if user_data_dir is None:
            user_data_dir = settings.chrome_profile_dir
        if window_size is None:
            window_size = (settings.window_width, settings.window_height)
        
        options = Options()
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
        
        # User agent
        options.add_argument(
            'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Optional headless mode
        if headless:
            options.add_argument('--headless=new')
        
        # Optional persistent profile
        if user_data_dir:
            options.add_argument(f'--user-data-dir={user_data_dir}')
        
        try:
            logger.info("creating_driver", headless=headless)
            
            # Use webdriver-manager to get correct ChromeDriver
            driver_path = ChromeDriverManager().install()
            
            driver = uc.Chrome(
                options=options,
                driver_executable_path=driver_path,
                version_main=None  # Auto-detect Chrome version
            )
            
            # Set page load timeout
            driver.set_page_load_timeout(settings.page_load_timeout)
            
            logger.info(
                "driver_created",
                version=driver.capabilities.get('browserVersion', 'unknown')
            )
            return driver
            
        except Exception as e:
            logger.error("driver_creation_failed", error=str(e), exc_info=True)
            raise