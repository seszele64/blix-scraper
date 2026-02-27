"""Date-filtered JSON storage implementation."""

from typing import TypeVar

import structlog
from pydantic import BaseModel

from src.domain.date_filter import DateFilterOptions

from .json_storage import JSONStorage

logger = structlog.get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class DateFilteredJSONStorage(JSONStorage[T]):
    """
    Storage handler with date filtering support.

    Extends JSONStorage to provide date-based filtering of entities
    using DateFilterOptions.
    """

    def load_all(  # type: ignore[override]
        self, date_filter: DateFilterOptions | None = None
    ) -> list[T]:
        """
        Load all entities from storage, optionally filtered by date.

        Args:
            date_filter: Optional date filter to apply to results

        Returns:
            List of entities, filtered if date_filter provided
        """
        # Load all entities without filter first
        entities = super().load_all()

        # Apply date filter if provided and has filter criteria
        if date_filter is not None and date_filter.has_date_filter():
            predicate = date_filter.to_predicate()
            total_count = len(entities)
            filtered_entities = [entity for entity in entities if predicate(entity)]

            logger.info(
                "date_filter_applied",
                total_entities=total_count,
                filtered_entities=len(filtered_entities),
                filter_active_on=date_filter.active_on,
                filter_date_from=date_filter.date_from or date_filter.valid_from,
                filter_date_to=date_filter.date_to or date_filter.valid_until,
            )

            return filtered_entities

        return entities

    def count(self, date_filter: DateFilterOptions | None = None) -> int:
        """
        Return count of entities, optionally filtered by date.

        Args:
            date_filter: Optional date filter to apply

        Returns:
            Count of entities (filtered if date_filter provided)
        """
        return len(self.load_all(date_filter))

    def exists(  # type: ignore[override]
        self, date_filter: DateFilterOptions | None = None
    ) -> bool:
        """
        Return True if any entities exist, optionally with date filter.

        Args:
            date_filter: Optional date filter to apply

        Returns:
            True if any entities exist (matching filter if provided)
        """
        return self.count(date_filter) > 0
