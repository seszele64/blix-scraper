"""Application configuration."""

from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RetrySettings(BaseSettings):
    """Retry configuration settings."""

    max_attempts: int = Field(default=3)
    backoff_factor: float = Field(default=2.0)
    jitter: bool = Field(default=True)


class ScrapingSettings(BaseSettings):
    """Hierarchical scraping configuration."""

    request_delay_min: float = Field(default=2.0)
    request_delay_max: float = Field(default=5.0)
    page_load_timeout: int = Field(default=30)
    retry: RetrySettings = Field(default_factory=RetrySettings)


class Settings(BaseSettings):
    """Main application settings."""

    # Paths
    # Deprecated: data_dir was used by JSONStorage which has been removed.
    # Kept for potential future persistence features.
    data_dir: Path = Path("data")
    cache_dir: Path = Path("data/cache")

    # WebDriver
    headless: bool = False
    chrome_profile_dir: str | None = None
    window_width: int = 1920
    window_height: int = 1080

    # Scraping (nested configuration)
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)

    # Logging
    log_level: str = "INFO"
    log_format: str = "console"  # or "json"

    # URLs
    base_url: str = "https://blix.pl"
    shops_url: str = "https://blix.pl/sklepy/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )

    @model_validator(mode="before")
    @classmethod
    def map_backwards_compatibility_fields(cls, values):
        """Map backwards compatibility fields to nested scraping config.

        This allows passing values like Settings(request_delay_min=0.5) directly
        while maintaining the nested scraping configuration structure.

        Uses dict-based construction to ensure Pydantic type coercion is applied
        to values from environment variables and .env files.
        """
        # Ensure scraping is a dict (not an already-constructed object)
        # to allow Pydantic to handle type coercion
        if "scraping" not in values:
            values["scraping"] = {}
        elif isinstance(values["scraping"], ScrapingSettings):
            # Convert existing ScrapingSettings to dict for merging
            values["scraping"] = values["scraping"].model_dump()

        # Handle request_delay_min
        if "request_delay_min" in values and values["request_delay_min"] is not None:
            values["scraping"]["request_delay_min"] = values.pop("request_delay_min")

        # Handle request_delay_max
        if "request_delay_max" in values and values["request_delay_max"] is not None:
            values["scraping"]["request_delay_max"] = values.pop("request_delay_max")

        # Handle page_load_timeout
        if "page_load_timeout" in values and values["page_load_timeout"] is not None:
            values["scraping"]["page_load_timeout"] = values.pop("page_load_timeout")

        # Handle retry settings
        if "retry" not in values["scraping"]:
            values["scraping"]["retry"] = {}
        elif isinstance(values["scraping"].get("retry"), RetrySettings):
            # Convert existing RetrySettings to dict for merging
            values["scraping"]["retry"] = values["scraping"]["retry"].model_dump()

        # Handle max_retries
        if "max_retries" in values and values["max_retries"] is not None:
            values["scraping"]["retry"]["max_attempts"] = values.pop("max_retries")

        # Handle retry_backoff
        if "retry_backoff" in values and values["retry_backoff"] is not None:
            values["scraping"]["retry"]["backoff_factor"] = values.pop("retry_backoff")

        return values

    @property
    def max_retries(self) -> int:
        """Backwards compatibility: maps to scraping.retry.max_attempts."""
        return self.scraping.retry.max_attempts

    @property
    def retry_backoff(self) -> float:
        """Backwards compatibility: maps to scraping.retry.backoff_factor."""
        return self.scraping.retry.backoff_factor

    @property
    def request_delay_min(self) -> float:
        """Backwards compatibility: maps to scraping.request_delay_min."""
        return self.scraping.request_delay_min

    @property
    def request_delay_max(self) -> float:
        """Backwards compatibility: maps to scraping.request_delay_max."""
        return self.scraping.request_delay_max

    @property
    def page_load_timeout(self) -> int:
        """Backwards compatibility: maps to scraping.page_load_timeout."""
        return self.scraping.page_load_timeout


settings = Settings()
