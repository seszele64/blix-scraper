"""Blix scraper package."""

__version__ = "0.3.0"

from src.config import settings
from src.services import ScraperService

__all__ = ["settings", "ScraperService"]
