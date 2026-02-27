"""Date filtering options for leaflets and offers."""

from datetime import datetime
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


class DateFilterOptions(BaseModel):
    """Filter options for date-based filtering of leaflets and offers.

    Supports multiple filtering strategies:
    - Single date: active_on - check if entity is valid on a specific date
    - Range start: valid_from / date_from - entities valid from this date onwards
    - Range end: valid_until / date_to - entities valid until this date
    - Range: date_from + date_to - entities valid within a date range

    Examples:
        >>> # Filter for leaflets active on a specific date
        >>> filter = DateFilterOptions(active_on=datetime(2024, 3, 15))
        >>>
        >>> # Filter for leaflets valid in a date range
        >>> filter = DateFilterOptions(
        ...     date_from=datetime(2024, 3, 1),
        ...     date_to=datetime(2024, 3, 31)
        ... )
        >>>
        >>> # Filter using alias fields
        >>> filter = DateFilterOptions(valid_from=datetime(2024, 3, 1))
    """

    active_on: Optional[datetime] = Field(
        default=None, description="Filter for leaflets/offers active on specific date"
    )
    valid_from: Optional[datetime] = Field(
        default=None, description="Filter for leaflets valid from this date"
    )
    valid_until: Optional[datetime] = Field(
        default=None, description="Filter for leaflets valid until this date"
    )
    date_from: Optional[datetime] = Field(
        default=None, description="Range start (alias for valid_from in range queries)"
    )
    date_to: Optional[datetime] = Field(
        default=None, description="Range end (alias for valid_until in range queries)"
    )

    def has_date_filter(self) -> bool:
        """Returns True if any date filter is set.

        Checks all filter fields including aliases to determine if any
        date-based filtering has been configured.

        Returns:
            True if any of the date filter fields is set, False otherwise
        """
        return any(
            [
                self.active_on is not None,
                self.valid_from is not None,
                self.valid_until is not None,
                self.date_from is not None,
                self.date_to is not None,
            ]
        )

    def to_predicate(self) -> Callable[[Any], bool]:
        """Returns a predicate function that checks if an entity matches the filter criteria.

        The predicate works with entities that have:
        - valid_from and valid_until attributes (like Leaflet, Offer, SearchResult)
        - Or entities that have an is_valid_on(date) method (like Leaflet)

        The predicate evaluates filters in this order:
        1. active_on - checks if entity is valid on the specific date
        2. date_from/valid_from - checks if entity starts on or after this date
        3. date_to/valid_until - checks if entity ends on or before this date
        4. All conditions must be satisfied (AND logic)

        Returns:
            A callable that takes an entity and returns True if it matches
            the filter criteria, False otherwise
        """
        # Resolve aliases: date_from maps to valid_from, date_to maps to valid_until
        resolved_date_from = self.date_from if self.date_from is not None else self.valid_from
        resolved_date_to = self.date_to if self.date_to is not None else self.valid_until

        def predicate(entity: Any) -> bool:
            # Handle active_on filter - check if entity is valid on specific date
            if self.active_on is not None:
                # Prefer is_valid_on method if available (e.g., Leaflet)
                is_valid_on_method = getattr(entity, "is_valid_on", None)
                if callable(is_valid_on_method):
                    # Call the method - it's guaranteed to return bool by Leaflet contract
                    return is_valid_on_method(self.active_on)  # type: ignore[no-any-return]
                # Fallback: check valid_from <= active_on <= valid_until
                if hasattr(entity, "valid_from") and hasattr(entity, "valid_until"):
                    return bool(entity.valid_from <= self.active_on <= entity.valid_until)
                # No date attributes to check against
                return False

            # Handle date range filters (date_from/valid_from and date_to/valid_until)
            if resolved_date_from is not None or resolved_date_to is not None:
                if not hasattr(entity, "valid_from") or not hasattr(entity, "valid_until"):
                    return False

                # Check lower bound (date_from/valid_from)
                if resolved_date_from is not None:
                    if entity.valid_from < resolved_date_from:
                        return False

                # Check upper bound (date_to/valid_until)
                if resolved_date_to is not None:
                    if entity.valid_until > resolved_date_to:
                        return False

            return True

        return predicate
