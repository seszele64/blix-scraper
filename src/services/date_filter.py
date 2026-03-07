"""Date filtering service for leaflet and offer filtering."""

from datetime import datetime, timezone
from typing import TypeVar

from ..domain.date_filter import DateFilterOptions

T = TypeVar("T")


class DateFilterService:
    """Service for filtering entities by date range.

    Provides methods to filter entities that have valid_from and valid_until
    attributes (like Leaflet, Offer, SearchResult) based on date criteria.
    """

    def filter_by_active_date(self, items: list[T], date: datetime) -> list[T]:
        """Filter items that are active on a specific date.

        Args:
            items: List of items to filter
            date: Target date to check activity

        Returns:
            List of items that are valid on the given date
        """
        return [item for item in items if self._is_valid_on(item, date)]

    def filter_by_date_range(self, items: list[T], start: datetime, end: datetime) -> list[T]:
        """Filter items that are valid within a date range.

        Args:
            items: List of items to filter
            start: Start of the date range
            end: End of the date range

        Returns:
            List of items that overlap with the given date range
        """
        result: list[T] = []
        for item in items:
            if self._is_valid_in_range(item, start, end):
                result.append(item)
        return result

    def filter_leaflets(self, leaflets: list[T], filter_options: DateFilterOptions) -> list[T]:
        """Filter leaflets using DateFilterOptions.

        Args:
            leaflets: List of Leaflet entities
            filter_options: Date filter configuration

        Returns:
            Filtered list of leaflets
        """
        if not filter_options.has_date_filter():
            return leaflets

        predicate = filter_options.to_predicate()
        return [leaflet for leaflet in leaflets if predicate(leaflet)]

    def _is_valid_on(self, item: T, target_date: datetime) -> bool:
        """Check if item is valid on target date.

        Args:
            item: Entity with valid_from/valid_until or is_valid_on method
            target_date: Date to check

        Returns:
            True if item is valid on the date
        """
        # Try is_valid_on method first (e.g., Leaflet)
        is_valid_on_method = getattr(item, "is_valid_on", None)
        if callable(is_valid_on_method):
            result = is_valid_on_method(target_date)
            return bool(result)

        # Fallback to valid_from/valid_until comparison
        if hasattr(item, "valid_from") and hasattr(item, "valid_until"):
            # Ensure target_date is timezone-aware
            target = target_date
            if target.tzinfo is None:
                target = target.replace(tzinfo=timezone.utc)

            valid_from = getattr(item, "valid_from")
            if valid_from.tzinfo is None:
                valid_from = valid_from.replace(tzinfo=timezone.utc)

            valid_until = getattr(item, "valid_until")
            if valid_until.tzinfo is None:
                valid_until = valid_until.replace(tzinfo=timezone.utc)

            return bool(valid_from <= target <= valid_until)

        return False

    def _is_valid_in_range(self, item: T, start: datetime, end: datetime) -> bool:
        """Check if item validity overlaps with date range.

        Args:
            item: Entity with valid_from/valid_until
            start: Start of range
            end: End of range

        Returns:
            True if item overlaps with the range
        """
        if not hasattr(item, "valid_from") or not hasattr(item, "valid_until"):
            return False

        # Ensure dates are timezone-aware
        start_date = start
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)

        end_date = end
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        valid_from = getattr(item, "valid_from")
        if valid_from.tzinfo is None:
            valid_from = valid_from.replace(tzinfo=timezone.utc)

        valid_until = getattr(item, "valid_until")
        if valid_until.tzinfo is None:
            valid_until = valid_until.replace(tzinfo=timezone.utc)

        # Check overlap: item starts before range ends AND ends after range starts
        return bool(valid_from <= end_date and valid_until >= start_date)
