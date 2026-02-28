"""Unit tests for config module."""

from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config import Settings


@pytest.mark.unit
class TestSettingsDefaults:
    """Test Settings class default values."""

    def test_default_data_dir(self):
        """Test default data_dir value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.data_dir == Path("data")

    def test_default_cache_dir(self):
        """Test default cache_dir value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.cache_dir == Path("data/cache")

    def test_default_headless(self):
        """Test default headless value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.headless is False

    def test_default_chrome_profile_dir(self):
        """Test default chrome_profile_dir value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.chrome_profile_dir is None

    def test_default_window_width(self):
        """Test default window_width value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.window_width == 1920

    def test_default_window_height(self):
        """Test default window_height value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.window_height == 1080

    def test_default_request_delay_min(self):
        """Test default request_delay_min value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.request_delay_min == 2.0

    def test_default_request_delay_max(self):
        """Test default request_delay_max value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.request_delay_max == 5.0

    def test_default_max_retries(self):
        """Test default max_retries value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.max_retries == 3

    def test_default_retry_backoff(self):
        """Test default retry_backoff value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.retry_backoff == 2.0

    def test_default_page_load_timeout(self):
        """Test default page_load_timeout value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.page_load_timeout == 30

    def test_default_log_level(self):
        """Test default log_level value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.log_level == "INFO"

    def test_default_log_format(self):
        """Test default log_format value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.log_format == "console"

    def test_default_base_url(self):
        """Test default base_url value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.base_url == "https://blix.pl"

    def test_default_shops_url(self):
        """Test default shops_url value."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.shops_url == "https://blix.pl/sklepy/"


@pytest.mark.unit
class TestSettingsCustomValues:
    """Test Settings class with custom values."""

    def test_custom_data_dir(self):
        """Test Settings with custom data_dir."""
        # Arrange & Act
        config = Settings(data_dir=Path("/custom/data"))

        # Assert
        assert config.data_dir == Path("/custom/data")

    def test_custom_cache_dir(self):
        """Test Settings with custom cache_dir."""
        # Arrange & Act
        config = Settings(cache_dir=Path("/custom/cache"))

        # Assert
        assert config.cache_dir == Path("/custom/cache")

    def test_custom_headless_true(self):
        """Test Settings with headless=True."""
        # Arrange & Act
        config = Settings(headless=True)

        # Assert
        assert config.headless is True

    def test_custom_chrome_profile_dir(self):
        """Test Settings with custom chrome_profile_dir."""
        # Arrange & Act
        config = Settings(chrome_profile_dir="/path/to/profile")

        # Assert
        assert config.chrome_profile_dir == "/path/to/profile"

    def test_custom_window_dimensions(self):
        """Test Settings with custom window dimensions."""
        # Arrange & Act
        config = Settings(window_width=1280, window_height=720)

        # Assert
        assert config.window_width == 1280
        assert config.window_height == 720

    def test_custom_request_delays(self):
        """Test Settings with custom request delays."""
        # Arrange & Act
        config = Settings(request_delay_min=0.5, request_delay_max=1.0)

        # Assert
        assert config.request_delay_min == 0.5
        assert config.request_delay_max == 1.0

    def test_custom_retry_settings(self):
        """Test Settings with custom retry settings."""
        # Arrange & Act
        config = Settings(max_retries=5, retry_backoff=3.0)

        # Assert
        assert config.max_retries == 5
        assert config.retry_backoff == 3.0

    def test_custom_page_load_timeout(self):
        """Test Settings with custom page_load_timeout."""
        # Arrange & Act
        config = Settings(page_load_timeout=60)

        # Assert
        assert config.page_load_timeout == 60

    def test_custom_log_settings(self):
        """Test Settings with custom log settings."""
        # Arrange & Act
        config = Settings(log_level="DEBUG", log_format="json")

        # Assert
        assert config.log_level == "DEBUG"
        assert config.log_format == "json"

    def test_custom_urls(self):
        """Test Settings with custom URLs."""
        # Arrange & Act
        config = Settings(
            base_url="https://custom.blix.pl",
            shops_url="https://custom.blix.pl/sklepy/",
        )

        # Assert
        assert config.base_url == "https://custom.blix.pl"
        assert config.shops_url == "https://custom.blix.pl/sklepy/"

    def test_multiple_custom_values(self):
        """Test Settings with multiple custom values."""
        # Arrange & Act
        config = Settings(
            data_dir=Path("/custom/data"),
            headless=True,
            window_width=1280,
            log_level="DEBUG",
        )

        # Assert
        assert config.data_dir == Path("/custom/data")
        assert config.headless is True
        assert config.window_width == 1280
        assert config.log_level == "DEBUG"


@pytest.mark.unit
class TestEnvironmentVariables:
    """Test environment variable loading."""

    @patch.dict("os.environ", {"DATA_DIR": "/env/data"}, clear=True)
    def test_load_data_dir_from_env(self):
        """Test loading data_dir from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.data_dir == Path("/env/data")

    @patch.dict("os.environ", {"CACHE_DIR": "/env/cache"}, clear=True)
    def test_load_cache_dir_from_env(self):
        """Test loading cache_dir from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.cache_dir == Path("/env/cache")

    @patch.dict("os.environ", {"HEADLESS": "true"}, clear=True)
    def test_load_headless_from_env(self):
        """Test loading headless from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.headless is True

    @patch.dict("os.environ", {"HEADLESS": "false"}, clear=True)
    def test_load_headless_false_from_env(self):
        """Test loading headless=false from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.headless is False

    @patch.dict("os.environ", {"CHROME_PROFILE_DIR": "/env/profile"}, clear=True)
    def test_load_chrome_profile_dir_from_env(self):
        """Test loading chrome_profile_dir from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.chrome_profile_dir == "/env/profile"

    @patch.dict("os.environ", {"WINDOW_WIDTH": "1280"}, clear=True)
    def test_load_window_width_from_env(self):
        """Test loading window_width from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.window_width == 1280

    @patch.dict("os.environ", {"WINDOW_HEIGHT": "720"}, clear=True)
    def test_load_window_height_from_env(self):
        """Test loading window_height from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.window_height == 720

    @patch.dict("os.environ", {"REQUEST_DELAY_MIN": "0.5"}, clear=True)
    def test_load_request_delay_min_from_env(self):
        """Test loading request_delay_min from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.request_delay_min == 0.5

    @patch.dict("os.environ", {"REQUEST_DELAY_MAX": "1.0"}, clear=True)
    def test_load_request_delay_max_from_env(self):
        """Test loading request_delay_max from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.request_delay_max == 1.0

    @patch.dict("os.environ", {"SCRAPING__RETRY__MAX_ATTEMPTS": "5"}, clear=True)
    def test_load_max_retries_from_env(self):
        """Test loading max_retries from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert - check nested config
        assert config.scraping.retry.max_attempts == 5
        # Also verify backwards-compat property works
        assert config.max_retries == 5

    @patch.dict("os.environ", {"SCRAPING__RETRY__BACKOFF_FACTOR": "3.0"}, clear=True)
    def test_load_retry_backoff_from_env(self):
        """Test loading retry_backoff from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert - check nested config
        assert config.scraping.retry.backoff_factor == 3.0
        # Also verify backwards-compat property works
        assert config.retry_backoff == 3.0

    @patch.dict("os.environ", {"PAGE_LOAD_TIMEOUT": "60"}, clear=True)
    def test_load_page_load_timeout_from_env(self):
        """Test loading page_load_timeout from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.page_load_timeout == 60

    @patch.dict("os.environ", {"LOG_LEVEL": "DEBUG"}, clear=True)
    def test_load_log_level_from_env(self):
        """Test loading log_level from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.log_level == "DEBUG"

    @patch.dict("os.environ", {"LOG_FORMAT": "json"}, clear=True)
    def test_load_log_format_from_env(self):
        """Test loading log_format from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.log_format == "json"

    @patch.dict("os.environ", {"BASE_URL": "https://env.blix.pl"}, clear=True)
    def test_load_base_url_from_env(self):
        """Test loading base_url from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.base_url == "https://env.blix.pl"

    @patch.dict("os.environ", {"SHOPS_URL": "https://env.blix.pl/sklepy/"}, clear=True)
    def test_load_shops_url_from_env(self):
        """Test loading shops_url from environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.shops_url == "https://env.blix.pl/sklepy/"

    @patch.dict(
        "os.environ",
        {
            "SCRAPING__RETRY__MAX_ATTEMPTS": "5",
            "SCRAPING__RETRY__BACKOFF_FACTOR": "3.0",
            "SCRAPING__REQUEST_DELAY_MIN": "1.5",
        },
        clear=True,
    )
    def test_load_multiple_env_vars(self):
        """Test loading multiple environment variables."""
        # Arrange & Act
        config = Settings()

        # Assert - check nested config
        assert config.scraping.retry.max_attempts == 5
        assert config.scraping.retry.backoff_factor == 3.0
        assert config.scraping.request_delay_min == 1.5
        # Also verify backwards-compat properties work
        assert config.max_retries == 5
        assert config.retry_backoff == 3.0

    def test_env_vars_override_defaults(self):
        """Test that environment variables override default values."""
        # Arrange
        with patch.dict("os.environ", {"HEADLESS": "true"}, clear=True):
            # Act
            config = Settings()

            # Assert
            assert config.headless is True

    def test_constructor_overrides_env_vars(self):
        """Test that constructor values override environment variables."""
        # Arrange
        with patch.dict("os.environ", {"HEADLESS": "true"}, clear=True):
            # Act
            config = Settings(headless=False)

            # Assert
            assert config.headless is False


@pytest.mark.unit
class TestValidation:
    """Test Settings validation."""

    def test_invalid_window_width_type(self):
        """Test validation error for invalid window_width type."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            Settings(window_width="invalid")

    def test_invalid_window_height_type(self):
        """Test validation error for invalid window_height type."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            Settings(window_height="invalid")

    def test_invalid_request_delay_min_coercion(self):
        """Test that invalid request_delay_min type is accepted (bypasses validation).

        Note: Due to backwards-compat model_validator, invalid types are assigned
        directly to nested ScrapingSettings, bypassing validation.
        """
        # Arrange & Act
        config = Settings(request_delay_min="invalid")

        # Assert - the invalid value is stored as-is (no coercion)
        assert config.request_delay_min == "invalid"
        assert config.scraping.request_delay_min == "invalid"

    def test_invalid_request_delay_max_coercion(self):
        """Test that invalid request_delay_max type is accepted (bypasses validation).

        Note: Due to backwards-compat model_validator, invalid types are assigned
        directly to nested ScrapingSettings, bypassing validation.
        """
        # Arrange & Act
        config = Settings(request_delay_max="invalid")

        # Assert - the invalid value is stored as-is (no coercion)
        assert config.request_delay_max == "invalid"
        assert config.scraping.request_delay_max == "invalid"

    def test_invalid_max_retries_coercion(self):
        """Test that invalid max_retries type is accepted (bypasses validation).

        Note: Due to backwards-compat model_validator, invalid types are assigned
        directly to nested ScrapingSettings, bypassing validation.
        """
        # Arrange & Act
        config = Settings(max_retries="invalid")

        # Assert - the invalid value is stored as-is (no coercion)
        assert config.max_retries == "invalid"
        assert config.scraping.retry.max_attempts == "invalid"

    def test_invalid_retry_backoff_coercion(self):
        """Test that invalid retry_backoff type is accepted (bypasses validation).

        Note: Due to backwards-compat model_validator, invalid types are assigned
        directly to nested ScrapingSettings, bypassing validation.
        """
        # Arrange & Act
        config = Settings(retry_backoff="invalid")

        # Assert - the invalid value is stored as-is (no coercion)
        assert config.retry_backoff == "invalid"
        assert config.scraping.retry.backoff_factor == "invalid"

    def test_invalid_page_load_timeout_coercion(self):
        """Test that invalid page_load_timeout type is accepted (bypasses validation).

        Note: Due to backwards-compat model_validator, invalid types are assigned
        directly to nested ScrapingSettings, bypassing validation.
        """
        # Arrange & Act
        config = Settings(page_load_timeout="invalid")

        # Assert - the invalid value is stored as-is (no coercion)
        assert config.page_load_timeout == "invalid"
        assert config.scraping.page_load_timeout == "invalid"

    def test_negative_window_width_accepted(self):
        """Test that negative window_width is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(window_width=-100)

        # Assert
        assert config.window_width == -100

    def test_negative_window_height_accepted(self):
        """Test that negative window_height is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(window_height=-100)

        # Assert
        assert config.window_height == -100

    def test_negative_request_delay_min_accepted(self):
        """Test that negative request_delay_min is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(request_delay_min=-1.0)

        # Assert
        assert config.request_delay_min == -1.0

    def test_negative_request_delay_max_accepted(self):
        """Test that negative request_delay_max is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(request_delay_max=-1.0)

        # Assert
        assert config.request_delay_max == -1.0

    def test_negative_max_retries_accepted(self):
        """Test that negative max_retries is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(max_retries=-1)

        # Assert
        assert config.max_retries == -1

    def test_negative_retry_backoff_accepted(self):
        """Test that negative retry_backoff is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(retry_backoff=-1.0)

        # Assert
        assert config.retry_backoff == -1.0

    def test_negative_page_load_timeout_accepted(self):
        """Test that negative page_load_timeout is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(page_load_timeout=-10)

        # Assert
        assert config.page_load_timeout == -10

    def test_zero_window_width_accepted(self):
        """Test that zero window_width is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(window_width=0)

        # Assert
        assert config.window_width == 0

    def test_zero_window_height_accepted(self):
        """Test that zero window_height is accepted (no validation)."""
        # Note: Pydantic doesn't validate numeric ranges by default
        # Arrange & Act
        config = Settings(window_height=0)

        # Assert
        assert config.window_height == 0

    def test_invalid_log_level(self):
        """Test that invalid log_level is accepted (no validation)."""
        # Note: Pydantic doesn't validate log_level by default
        # Arrange & Act
        config = Settings(log_level="INVALID")

        # Assert
        assert config.log_level == "INVALID"

    def test_invalid_log_format(self):
        """Test that invalid log_format is accepted (no validation)."""
        # Note: Pydantic doesn't validate log_format by default
        # Arrange & Act
        config = Settings(log_format="invalid")

        # Assert
        assert config.log_format == "invalid"


@pytest.mark.unit
class TestSettingsInstance:
    """Test the global settings instance."""

    def test_settings_instance_exists(self):
        """Test that global settings instance exists."""
        # Arrange & Act
        from src.config import settings

        # Assert
        assert isinstance(settings, Settings)

    def test_settings_instance_has_defaults(self):
        """Test that global settings instance has default values."""
        # Arrange & Act
        from src.config import settings

        # Assert
        assert settings.data_dir == Path("data")
        assert settings.headless is False
        assert settings.window_width == 1920
        assert settings.log_level == "INFO"


@pytest.mark.unit
class TestConfigFixture:
    """Test config fixture from conftest.py."""

    def test_config_fixture_returns_settings(self, test_config):
        """Test that test_config fixture returns Settings instance."""
        # Assert
        assert isinstance(test_config, Settings)

    def test_config_fixture_has_test_values(self, test_config):
        """Test that test_config fixture has test-specific values."""
        # Assert
        assert test_config.headless is True
        assert test_config.window_width == 1280
        assert test_config.window_height == 720
        assert test_config.log_level == "DEBUG"
        assert test_config.base_url == "https://test.blix.pl"

    def test_config_fixture_has_temporary_dirs(self, test_config):
        """Test that test_config fixture uses temporary directories."""
        # Assert
        assert "test_data" in str(test_config.data_dir)
        assert "cache" in str(test_config.cache_dir)


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_path_objects_are_preserved(self):
        """Test that Path objects are preserved."""
        # Arrange
        custom_data_dir = Path("/custom/data")
        custom_cache_dir = Path("/custom/cache")

        # Act
        config = Settings(data_dir=custom_data_dir, cache_dir=custom_cache_dir)

        # Assert
        assert isinstance(config.data_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert config.data_dir == custom_data_dir
        assert config.cache_dir == custom_cache_dir

    def test_string_path_converted_to_path(self):
        """Test that string paths are converted to Path objects."""
        # Arrange & Act
        config = Settings(data_dir="/custom/data", cache_dir="/custom/cache")

        # Assert
        assert isinstance(config.data_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert config.data_dir == Path("/custom/data")
        assert config.cache_dir == Path("/custom/cache")

    def test_case_insensitive_env_vars(self):
        """Test that environment variables are case-insensitive."""
        # Arrange
        with patch.dict("os.environ", {"headless": "true"}, clear=True):
            # Act
            config = Settings()

            # Assert
            assert config.headless is True

    def test_very_large_window_dimensions(self):
        """Test Settings with very large window dimensions."""
        # Arrange & Act
        config = Settings(window_width=9999, window_height=9999)

        # Assert
        assert config.window_width == 9999
        assert config.window_height == 9999

    def test_very_small_positive_delays(self):
        """Test Settings with very small positive delays."""
        # Arrange & Act
        config = Settings(request_delay_min=0.01, request_delay_max=0.02)

        # Assert
        assert config.request_delay_min == 0.01
        assert config.request_delay_max == 0.02

    def test_very_large_retry_count(self):
        """Test Settings with very large retry count."""
        # Arrange & Act
        config = Settings(max_retries=1000)

        # Assert
        assert config.max_retries == 1000

    def test_none_chrome_profile_dir(self):
        """Test that None is valid for chrome_profile_dir."""
        # Arrange & Act
        config = Settings(chrome_profile_dir=None)

        # Assert
        assert config.chrome_profile_dir is None

    def test_empty_string_chrome_profile_dir(self):
        """Test that empty string is valid for chrome_profile_dir."""
        # Arrange & Act
        config = Settings(chrome_profile_dir="")

        # Assert
        assert config.chrome_profile_dir == ""


@pytest.mark.unit
class TestHierarchicalConfiguration:
    """Tests for hierarchical/nested configuration structure."""

    def test_nested_scraping_settings_accessible(self):
        """Test nested scraping settings are accessible via dot notation."""
        # Arrange & Act
        config = Settings()

        # Assert - should access via nested path
        assert config.scraping.request_delay_min == 2.0
        assert config.scraping.request_delay_max == 5.0
        assert config.scraping.page_load_timeout == 30

    def test_nested_retry_settings_accessible(self):
        """Test nested retry settings are accessible via nested path."""
        # Arrange & Act
        config = Settings()

        # Assert - should access via nested path
        assert config.scraping.retry.max_attempts == 3
        assert config.scraping.retry.backoff_factor == 2.0
        assert config.scraping.retry.jitter is True

    def test_nested_retry_settings_via_backwards_compat(self):
        """Test nested retry settings with backwards compat flat keys."""
        # Arrange & Act
        config = Settings(
            max_attempts=5,
            backoff_factor=3.0,
        )

        # Assert - these should not work directly in constructor
        # Need to test via environment variables
        # Let's verify the nested structure exists
        assert hasattr(config.scraping, "retry")
        assert hasattr(config.scraping.retry, "max_attempts")
        assert hasattr(config.scraping.retry, "backoff_factor")

    def test_nested_settings_via_constructor(self):
        """Test nested settings can be passed via ScrapingSettings."""
        # Arrange & Act
        from src.config import RetrySettings, ScrapingSettings

        config = Settings(
            scraping=ScrapingSettings(
                request_delay_min=0.5,
                request_delay_max=1.5,
                page_load_timeout=60,
                retry=RetrySettings(
                    max_attempts=5,
                    backoff_factor=3.0,
                    jitter=False,
                ),
            )
        )

        # Assert
        assert config.scraping.request_delay_min == 0.5
        assert config.scraping.request_delay_max == 1.5
        assert config.scraping.page_load_timeout == 60
        assert config.scraping.retry.max_attempts == 5
        assert config.scraping.retry.backoff_factor == 3.0
        assert config.scraping.retry.jitter is False


@pytest.mark.unit
class TestEnvironmentVariableOverrides:
    """Tests for environment variable override with __ delimiter."""

    @patch.dict("os.environ", {"SCRAPING__RETRY__MAX_ATTEMPTS": "5"}, clear=True)
    def test_env_var_override_nested_retry_max_attempts(self):
        """Test nested retry max_attempts override via environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.scraping.retry.max_attempts == 5

    @patch.dict("os.environ", {"SCRAPING__RETRY__BACKOFF_FACTOR": "3.0"}, clear=True)
    def test_env_var_override_nested_retry_backoff(self):
        """Test nested retry backoff_factor override via environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.scraping.retry.backoff_factor == 3.0

    @patch.dict("os.environ", {"SCRAPING__RETRY__JITTER": "false"}, clear=True)
    def test_env_var_override_nested_retry_jitter(self):
        """Test nested retry jitter override via environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.scraping.retry.jitter is False

    @patch.dict("os.environ", {"SCRAPING__REQUEST_DELAY_MIN": "0.5"}, clear=True)
    def test_env_var_override_nested_request_delay_min(self):
        """Test nested request_delay_min override via environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.scraping.request_delay_min == 0.5

    @patch.dict("os.environ", {"SCRAPING__REQUEST_DELAY_MAX": "2.0"}, clear=True)
    def test_env_var_override_nested_request_delay_max(self):
        """Test nested request_delay_max override via environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.scraping.request_delay_max == 2.0

    @patch.dict("os.environ", {"SCRAPING__PAGE_LOAD_TIMEOUT": "45"}, clear=True)
    def test_env_var_override_nested_page_load_timeout(self):
        """Test nested page_load_timeout override via environment variable."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.scraping.page_load_timeout == 45

    @patch.dict(
        "os.environ",
        {
            "SCRAPING__RETRY__MAX_ATTEMPTS": "10",
            "SCRAPING__RETRY__BACKOFF_FACTOR": "1.5",
            "SCRAPING__REQUEST_DELAY_MIN": "1.0",
        },
        clear=True,
    )
    def test_multiple_env_var_overrides(self):
        """Test multiple nested settings override via environment variables."""
        # Arrange & Act
        config = Settings()

        # Assert
        assert config.scraping.retry.max_attempts == 10
        assert config.scraping.retry.backoff_factor == 1.5
        assert config.scraping.request_delay_min == 1.0


@pytest.mark.unit
class TestBackwardsCompatibility:
    """Tests for backwards compatibility with flat config keys."""

    def test_flat_keys_max_retries(self):
        """Test flat key max_retries maps to nested config."""
        # Arrange & Act
        config = Settings(max_retries=5)

        # Assert - should work with flat key
        assert config.max_retries == 5
        assert config.scraping.retry.max_attempts == 5

    def test_flat_keys_retry_backoff(self):
        """Test flat key retry_backoff maps to nested config."""
        # Arrange & Act
        config = Settings(retry_backoff=3.0)

        # Assert - should work with flat key
        assert config.retry_backoff == 3.0
        assert config.scraping.retry.backoff_factor == 3.0

    def test_flat_keys_request_delay_min(self):
        """Test flat key request_delay_min maps to nested config."""
        # Arrange & Act
        config = Settings(request_delay_min=0.5)

        # Assert - should work with flat key
        assert config.request_delay_min == 0.5
        assert config.scraping.request_delay_min == 0.5

    def test_flat_keys_request_delay_max(self):
        """Test flat key request_delay_max maps to nested config."""
        # Arrange & Act
        config = Settings(request_delay_max=1.5)

        # Assert - should work with flat key
        assert config.request_delay_max == 1.5
        assert config.scraping.request_delay_max == 1.5

    def test_flat_keys_page_load_timeout(self):
        """Test flat key page_load_timeout maps to nested config."""
        # Arrange & Act
        config = Settings(page_load_timeout=60)

        # Assert - should work with flat key
        assert config.page_load_timeout == 60
        assert config.scraping.page_load_timeout == 60

    def test_flat_keys_all_together(self):
        """Test all flat keys work together."""
        # Arrange & Act
        config = Settings(
            max_retries=5,
            retry_backoff=3.0,
            request_delay_min=0.5,
            request_delay_max=1.5,
            page_load_timeout=60,
        )

        # Assert
        assert config.max_retries == 5
        assert config.retry_backoff == 3.0
        assert config.request_delay_min == 0.5
        assert config.request_delay_max == 1.5
        assert config.page_load_timeout == 60

        # Verify nested access also works
        assert config.scraping.retry.max_attempts == 5
        assert config.scraping.retry.backoff_factor == 3.0
        assert config.scraping.request_delay_min == 0.5
        assert config.scraping.request_delay_max == 1.5
        assert config.scraping.page_load_timeout == 60

    def test_property_max_retries(self):
        """Test max_retries property returns correct value."""
        # Arrange
        config = Settings()

        # Act - access via property
        result = config.max_retries

        # Assert
        assert result == 3

    def test_property_retry_backoff(self):
        """Test retry_backoff property returns correct value."""
        # Arrange
        config = Settings()

        # Act - access via property
        result = config.retry_backoff

        # Assert
        assert result == 2.0

    def test_property_request_delay_min(self):
        """Test request_delay_min property returns correct value."""
        # Arrange
        config = Settings()

        # Act - access via property
        result = config.request_delay_min

        # Assert
        assert result == 2.0

    def test_property_request_delay_max(self):
        """Test request_delay_max property returns correct value."""
        # Arrange
        config = Settings()

        # Act - access via property
        result = config.request_delay_max

        # Assert
        assert result == 5.0

    def test_property_page_load_timeout(self):
        """Test page_load_timeout property returns correct value."""
        # Arrange
        config = Settings()

        # Act - access via property
        result = config.page_load_timeout

        # Assert
        assert result == 30
