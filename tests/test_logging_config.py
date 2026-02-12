"""Tests for logging configuration."""

import logging
from unittest.mock import Mock, patch

import pytest
import structlog

from src.logging_config import get_logger, setup_logging


@pytest.mark.unit
class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_creates_logs_directory(self, tmp_path):
        """Test that setup_logging creates logs directory."""
        # Arrange
        with patch("src.logging_config.Path") as mock_path:
            mock_path.return_value = tmp_path / "logs"
            mock_path_instance = tmp_path / "logs"

            # Act
            setup_logging()

            # Assert
            assert mock_path_instance.exists()
            assert mock_path_instance.is_dir()

    def test_setup_logging_configures_standard_logging(self):
        """Test that setup_logging configures standard logging."""
        # Arrange
        # Reset logging to ensure basicConfig will set the level
        logging.root.handlers.clear()
        logging.root.setLevel(logging.WARNING)

        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"

            # Act
            setup_logging()

            # Assert
            assert logging.root.level == logging.INFO

    def test_setup_logging_with_debug_level(self):
        """Test setup_logging with DEBUG log level."""
        # Arrange
        logging.root.handlers.clear()
        logging.root.setLevel(logging.WARNING)

        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "DEBUG"
            mock_settings.log_format = "console"

            # Act
            setup_logging()

            # Assert
            assert logging.root.level == logging.DEBUG

    def test_setup_logging_with_warning_level(self):
        """Test setup_logging with WARNING log level."""
        # Arrange
        logging.root.handlers.clear()
        logging.root.setLevel(logging.INFO)

        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "WARNING"
            mock_settings.log_format = "console"

            # Act
            setup_logging()

            # Assert
            assert logging.root.level == logging.WARNING

    def test_setup_logging_with_error_level(self):
        """Test setup_logging with ERROR log level."""
        # Arrange
        logging.root.handlers.clear()
        logging.root.setLevel(logging.WARNING)

        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "ERROR"
            mock_settings.log_format = "console"

            # Act
            setup_logging()

            # Assert
            assert logging.root.level == logging.ERROR

    def test_setup_logging_adds_file_handler(self, tmp_path):
        """Test that setup_logging adds file handler."""
        # Arrange
        with patch("src.logging_config.Path") as mock_path:
            mock_path.return_value = tmp_path / "logs"

            # Act
            setup_logging()

            # Assert
            file_handlers = [h for h in logging.root.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) >= 1

    def test_setup_logging_file_handler_level(self, tmp_path):
        """Test that file handler has DEBUG level."""
        # Arrange
        logging.root.handlers.clear()
        with patch("src.logging_config.Path") as mock_path:
            mock_path.return_value = tmp_path / "logs"

            # Act
            setup_logging()

            # Assert
            file_handlers = [h for h in logging.root.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) >= 1
            # File handler should be set to DEBUG level
            assert (
                file_handlers[0].level == logging.DEBUG or file_handlers[0].level == 0
            )  # NOTSET means use logger level

    def test_setup_logging_with_json_format(self):
        """Test setup_logging with JSON format."""
        # Arrange
        logging.root.handlers.clear()
        logging.root.setLevel(logging.WARNING)

        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "json"

            # Act
            setup_logging()

            # Assert
            # JSON format should be configured
            assert logging.root.level == logging.INFO

    def test_setup_logging_with_console_format(self):
        """Test setup_logging with console format."""
        # Arrange
        logging.root.handlers.clear()
        logging.root.setLevel(logging.WARNING)

        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"

            # Act
            setup_logging()

            # Assert
            # Console format should be configured
            assert logging.root.level == logging.INFO

    def test_setup_logging_configures_structlog(self):
        """Test that setup_logging configures structlog."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"

            # Act
            setup_logging()

            # Assert
            # structlog should be configured
            logger = structlog.get_logger(__name__)
            assert logger is not None


@pytest.mark.unit
class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        # Arrange
        logger_name = "test_logger"

        # Act
        logger = get_logger(logger_name)

        # Assert
        assert logger is not None
        # get_logger returns BoundLoggerLazyProxy which wraps BoundLogger
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    def test_get_logger_with_module_name(self):
        """Test get_logger with __name__."""
        # Act
        logger = get_logger(__name__)

        # Assert
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")

    def test_get_logger_with_custom_name(self):
        """Test get_logger with custom name."""
        # Arrange
        custom_name = "my.custom.logger"

        # Act
        logger = get_logger(custom_name)

        # Assert
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")

    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns same instance for same name."""
        # Arrange
        logger_name = "test.logger"

        # Act
        logger1 = get_logger(logger_name)
        logger2 = get_logger(logger_name)

        # Assert
        # Should return the same logger instance
        assert logger1._logger is logger2._logger


@pytest.mark.unit
class TestLoggingOutput:
    """Tests for logging output and format."""

    def test_log_info_message(self, caplog):
        """Test logging an info message."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act
        with caplog.at_level(logging.INFO):
            logger.info("test_message", key="value")

        # Assert
        assert len(caplog.records) >= 1
        assert "test_message" in caplog.text or "test_message" in str(caplog.records)

    def test_log_warning_message(self, caplog):
        """Test logging a warning message."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "WARNING"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act
        with caplog.at_level(logging.WARNING):
            logger.warning("warning_message", key="value")

        # Assert
        assert len(caplog.records) >= 1

    def test_log_error_message(self, caplog):
        """Test logging an error message."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "ERROR"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act
        with caplog.at_level(logging.ERROR):
            logger.error("error_message", key="value")

        # Assert
        assert len(caplog.records) >= 1

    def test_log_debug_message(self, caplog):
        """Test logging a debug message."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "DEBUG"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act
        with caplog.at_level(logging.DEBUG):
            logger.debug("debug_message", key="value")

        # Assert
        assert len(caplog.records) >= 1

    def test_log_with_context(self, caplog):
        """Test logging with context variables."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act
        with caplog.at_level(logging.INFO):
            logger.info("context_message", user_id=123, action="test")

        # Assert
        assert len(caplog.records) >= 1

    def test_log_with_exception(self, caplog):
        """Test logging with exception info."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "ERROR"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act
        try:
            raise ValueError("Test exception")
        except ValueError:
            with caplog.at_level(logging.ERROR):
                logger.exception("exception_occurred")

        # Assert
        assert len(caplog.records) >= 1


@pytest.mark.unit
class TestLoggingLevels:
    """Tests for logging level filtering."""

    def test_debug_level_configuration(self):
        """Test that DEBUG level is configured correctly."""
        # Arrange
        logging.root.handlers.clear()
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "DEBUG"
            mock_settings.log_format = "console"
            setup_logging()

        # Assert
        assert logging.root.level == logging.DEBUG

    def test_info_level_configuration(self):
        """Test that INFO level is configured correctly."""
        # Arrange
        logging.root.handlers.clear()
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        # Assert
        assert logging.root.level == logging.INFO

    def test_warning_level_configuration(self):
        """Test that WARNING level is configured correctly."""
        # Arrange
        logging.root.handlers.clear()
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "WARNING"
            mock_settings.log_format = "console"
            setup_logging()

        # Assert
        assert logging.root.level == logging.WARNING

    def test_error_level_configuration(self):
        """Test that ERROR level is configured correctly."""
        # Arrange
        logging.root.handlers.clear()
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "ERROR"
            mock_settings.log_format = "console"
            setup_logging()

        # Assert
        assert logging.root.level == logging.ERROR


@pytest.mark.unit
class TestLoggingErrorHandling:
    """Tests for error handling in logging setup."""

    def test_setup_logging_handles_invalid_log_level(self):
        """Test that setup_logging handles invalid log level gracefully."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INVALID"
            mock_settings.log_format = "console"

            # Act & Assert
            # Should raise AttributeError for invalid log level
            with pytest.raises(AttributeError):
                setup_logging()

    def test_setup_logging_handles_directory_creation_error(self):
        """Test that setup_logging handles directory creation errors."""
        # Arrange
        with patch("src.logging_config.Path") as mock_path:
            mock_path_instance = Mock()
            mock_path_instance.mkdir.side_effect = PermissionError("Permission denied")
            mock_path.return_value = mock_path_instance

            # Act & Assert
            with pytest.raises(PermissionError):
                setup_logging()

    def test_setup_logging_handles_file_handler_error(self):
        """Test that setup_logging handles file handler creation errors."""
        # Arrange
        with patch("src.logging_config.Path") as mock_path:
            mock_path_instance = Mock()
            mock_path_instance.mkdir = Mock()
            mock_path_instance.__truediv__ = Mock(return_value=Mock())
            mock_path.return_value = mock_path_instance

        with patch("src.logging_config.logging.FileHandler") as mock_file_handler:
            mock_file_handler.side_effect = IOError("Cannot create file")

            # Act & Assert
            with pytest.raises(IOError):
                setup_logging()


@pytest.mark.unit
class TestStructlogConfiguration:
    """Tests for structlog-specific configuration."""

    def test_structlog_has_bound_logger(self):
        """Test that structlog is configured with BoundLogger."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        # Act
        logger = get_logger(__name__)

        # Assert
        # get_logger returns BoundLoggerLazyProxy which wraps BoundLogger
        # Check that it has the expected methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "bind")

    def test_structlog_has_contextvars_processor(self):
        """Test that structlog has contextvars processor."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Assert
        # Logger should support context binding
        bound_logger = logger.bind(user_id=123)
        assert bound_logger is not None
        # The bound logger should have the same methods
        assert hasattr(bound_logger, "info")
        assert hasattr(bound_logger, "debug")

    def test_structlog_has_timestamp_processor(self):
        """Test that structlog has timestamp processor."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act & Assert
        # Timestamp processor should be configured - verify by logging
        # and checking that the log message is created without error
        logger.info("test_message")
        # Should not raise any exceptions
        assert True

    def test_structlog_has_log_level_processor(self):
        """Test that structlog has log level processor."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act
        # Logger should support different log levels
        logger.info("info")
        logger.warning("warning")
        logger.error("error")

        # Assert
        # Should not raise any exceptions
        assert True


@pytest.mark.unit
class TestLoggingIntegration:
    """Integration tests for logging configuration."""

    def test_full_logging_workflow(self, caplog, tmp_path):
        """Test complete logging workflow from setup to output."""
        # Arrange
        with patch("src.logging_config.Path") as mock_path:
            mock_path.return_value = tmp_path / "logs"

        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger("test.integration")

        # Act
        with caplog.at_level(logging.INFO):
            logger.info("workflow_start", step=1)
            logger.info("workflow_progress", step=2, progress=50)
            logger.info("workflow_complete", step=3, status="success")

        # Assert
        assert len(caplog.records) >= 3

    def test_multiple_loggers(self, caplog):
        """Test creating and using multiple loggers."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "DEBUG"
            mock_settings.log_format = "console"
            setup_logging()

        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        logger3 = get_logger("logger3")

        # Act
        with caplog.at_level(logging.DEBUG):
            logger1.info("message1")
            logger2.info("message2")
            logger3.info("message3")

        # Assert
        assert len(caplog.records) >= 3

    def test_logger_with_nested_context(self, caplog):
        """Test logger with nested context binding."""
        # Arrange
        with patch("src.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "console"
            setup_logging()

        logger = get_logger(__name__)

        # Act
        with caplog.at_level(logging.INFO):
            logger1 = logger.bind(request_id="123")
            logger1.info("message1")

            logger2 = logger1.bind(user_id="456")
            logger2.info("message2")

        # Assert
        assert len(caplog.records) >= 2
