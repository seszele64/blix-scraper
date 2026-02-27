"""Field filtering for selective JSON storage."""

from dataclasses import fields, is_dataclass
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel


class FieldFilter:
    """Filter entities to include only specified fields."""

    # Base schema - commonly useful fields
    BASE_SCHEMA = {
        "name",
        "shop_name",
        "brand_name",
        "price",
        "percent_discount",
        "valid_from",
        "valid_until",
    }

    def __init__(self, include_fields: Optional[Set[str]] = None, use_base: bool = True):
        """
        Initialize field filter.

        Args:
            include_fields: Specific fields to include. If None, uses base schema.
            use_base: If True, start with base schema and add extra fields.
        """
        if include_fields is None:
            self.fields = self.BASE_SCHEMA.copy()
        elif use_base:
            self.fields = self.BASE_SCHEMA | include_fields
        else:
            self.fields = include_fields

    def filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter a dictionary to include only specified fields.

        Args:
            data: Dictionary to filter

        Returns:
            Filtered dictionary
        """
        return {k: v for k, v in data.items() if k in self.fields}

    def filter_entity(self, entity: Any) -> Dict[str, Any]:
        """
        Filter an entity (Pydantic model or dataclass) to include only specified fields.

        Args:
            entity: Entity to filter

        Returns:
            Filtered dictionary representation
        """
        # Handle Pydantic models
        if isinstance(entity, BaseModel):
            full_dict = entity.model_dump()
            return self.filter_dict(full_dict)

        # Handle dataclasses
        if is_dataclass(entity):
            full_dict = {f.name: getattr(entity, f.name) for f in fields(entity)}
            return self.filter_dict(full_dict)

        # Handle plain dicts
        if isinstance(entity, dict):
            return self.filter_dict(entity)

        # Fallback: try __dict__
        if hasattr(entity, "__dict__"):
            return self.filter_dict(entity.__dict__)

        raise TypeError(f"Cannot filter entity of type {type(entity)}")

    def filter_many(self, entities: List[Any]) -> List[Dict[str, Any]]:
        """
        Filter multiple entities.

        Args:
            entities: List of entities to filter

        Returns:
            List of filtered dictionaries
        """
        return [self.filter_entity(entity) for entity in entities]

    @classmethod
    def minimal(cls) -> "FieldFilter":
        """
        Create filter with minimal fields (name, price, shop).

        Returns:
            FieldFilter with minimal schema
        """
        return cls({"name", "price", "shop_name"}, use_base=False)

    @classmethod
    def with_dates(cls) -> "FieldFilter":
        """
        Create filter with base schema (includes dates).

        Returns:
            FieldFilter with base schema
        """
        return cls(use_base=True)

    @classmethod
    def custom(cls, *field_names: str) -> "FieldFilter":
        """
        Create filter with custom fields only.

        Args:
            *field_names: Field names to include

        Returns:
            FieldFilter with custom schema
        """
        return cls(set(field_names), use_base=False)

    @classmethod
    def extended(cls, *extra_fields: str) -> "FieldFilter":
        """
        Create filter with base schema plus extra fields.

        Args:
            *extra_fields: Additional field names to include

        Returns:
            FieldFilter with extended schema
        """
        return cls(set(extra_fields), use_base=True)
