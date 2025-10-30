"""Helper utilities for Selenium WebDriver."""

from typing import Optional
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
import time
import random
import structlog

from ..config import settings

logger = structlog.get_logger(__name__)


def human_delay(
    min_sec: Optional[float] = None,
    max_sec: Optional[float] = None
) -> None:
    """
    Random delay to simulate human behavior.
    
    Args:
        min_sec: Minimum delay in seconds (None = use settings)
        max_sec: Maximum delay in seconds (None = use settings)
    """
    if min_sec is None:
        min_sec = settings.request_delay_min
    if max_sec is None:
        max_sec = settings.request_delay_max
    
    delay = random.uniform(min_sec, max_sec)
    logger.debug("human_delay", delay_seconds=delay)
    time.sleep(delay)


def wait_for_element(
    driver: WebDriver,
    by: By,
    value: str,
    timeout: int = 10
) -> WebElement:
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
        logger.debug("element_found", by=by.name, value=value)
        return element
    except TimeoutException:
        logger.error("element_not_found", by=by.name, value=value, timeout=timeout)
        raise TimeoutException(f"Element not found: {by}={value}")


def wait_for_elements(
    driver: WebDriver,
    by: By,
    value: str,
    timeout: int = 10
) -> list[WebElement]:
    """
    Wait for multiple elements to be present in DOM.
    
    Args:
        driver: Selenium WebDriver instance
        by: Locator strategy
        value: Selector value
        timeout: Max wait time in seconds
        
    Returns:
        List of WebElements
        
    Raises:
        TimeoutException if not found
    """
    try:
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
        logger.debug("elements_found", by=by.name, value=value, count=len(elements))
        return elements
    except TimeoutException:
        logger.error("elements_not_found", by=by.name, value=value, timeout=timeout)
        raise TimeoutException(f"Elements not found: {by}={value}")


def scroll_to_bottom(driver: WebDriver, pause_time: float = 1.0) -> None:
    """
    Scroll to bottom of page to trigger lazy loading.
    
    Args:
        driver: Selenium WebDriver instance
        pause_time: Pause between scrolls (seconds)
    """
    logger.debug("scrolling_to_bottom")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        
        # Calculate new height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            logger.debug("reached_bottom")
            break
        
        last_height = new_height


def scroll_to_element(driver: WebDriver, element: WebElement) -> None:
    """
    Scroll element into view.
    
    Args:
        driver: Selenium WebDriver instance
        element: Target element
    """
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)  # Brief pause after scroll