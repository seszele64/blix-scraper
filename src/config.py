"""Application configuration."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Paths
    data_dir: Path = Path("data")
    cache_dir: Path = Path("data/cache")

    # WebDriver
    headless: bool = False
    chrome_profile_dir: Optional[str] = None
    window_width: int = 1920
    window_height: int = 1080

    # Scraping
    request_delay_min: float = 2.0
    request_delay_max: float = 5.0
    max_retries: int = 3
    retry_backoff: float = 2.0
    page_load_timeout: int = 30

    # Logging
    log_level: str = "INFO"
    log_format: str = "console"  # or "json"

    # URLs
    base_url: str = "https://blix.pl"
    shops_url: str = "https://blix.pl/sklepy/"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


settings = Settings()
