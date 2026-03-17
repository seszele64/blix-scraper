"""Logging configuration using structlog."""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog

from .config import settings


def setup_logging() -> None:
    """
    Configure structlog for the application.

    Sets up:
    - Console output with colors (dev mode)
    - JSON output (production mode)
    - Log level from settings
    - File output to logs directory
    """
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s", stream=sys.stdout, level=getattr(logging, settings.log_level.upper())
    )

    # Add file handler
    file_handler = logging.FileHandler(logs_dir / "blix-scraper.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    logging.root.addHandler(file_handler)

    # Structlog processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_format == "json":
        # JSON output for production
        processors = shared_processors + [
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console output with colors for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Structlog logger instance
    """
    return structlog.get_logger(name)
