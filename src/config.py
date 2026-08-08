"""Application configuration."""

from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

FIELD_MAP: dict[str, str] = {
    "request_delay_min": "request_delay_min",
    "request_delay_max": "request_delay_max",
    "page_load_timeout": "page_load_timeout",
    "max_retries": "retry.max_attempts",
    "retry_backoff": "retry.backoff_factor",
}


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

        Flat keys are mapped into the scraping dict as raw values. Pydantic
        handles all type coercion and validation during normal construction.
        """
        # Normalize scraping to a plain dict for mutation
        if "scraping" not in values or values["scraping"] is None:
            values["scraping"] = {}
        elif isinstance(values["scraping"], ScrapingSettings):
            values["scraping"] = values["scraping"].model_dump()

        # Map each flat key into the nested dict structure
        for flat_key, nested_path in FIELD_MAP.items():
            if flat_key in values:
                parts = nested_path.split(".")
                target = values["scraping"]
                for part in parts[:-1]:
                    if part not in target or target[part] is None:
                        target[part] = {}
                    elif isinstance(target[part], (ScrapingSettings, RetrySettings)):
                        target[part] = target[part].model_dump()
                    target = target[part]
                target[parts[-1]] = values.pop(flat_key)

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
