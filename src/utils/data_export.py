"""Data export utilities for saving scraped data to JSON files."""

import difflib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import platformdirs
except ImportError:
    platformdirs = None  # type: ignore[assignment]

from src.domain.entities import Keyword, Leaflet, Offer, SearchResult, Shop
from src.logging_config import get_logger

logger = get_logger(__name__)

# Schema version for exports
EXPORT_SCHEMA_VERSION = "1.0.0"

# Tool info
TOOL_NAME = "blix-scraper"

# Entity type mappings
ENTITY_TYPE_MAP = {
    "scrape_shops": "shops",
    "search": "search_results",
    "scrape_leaflets": "leaflets",
    "scrape_offers": "offers",
    "scrape_full_shop": "full_shop",
}

# Default filename prefixes
FILENAME_PREFIX_MAP = {
    "scrape_shops": "shops",
    "search": "search_results",
    "scrape_leaflets": "leaflets",
    "scrape_offers": "offers",
    "scrape_full_shop": "full_shop",
}


def get_version() -> str:
    """Get the tool version from pyproject.toml.

    Returns:
        Version string or 'unknown' if not available.
    """
    try:
        from importlib.metadata import version

        return version("blix-scraper")
    except Exception:
        pass

    # Try to read from pyproject.toml directly
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if match:
            return match.group(1)

    return "unknown"


def get_default_data_dir() -> Path:
    """Get the default data directory using XDG Base Directory spec.

    Returns:
        Path to the default data directory.
    """
    if platformdirs is not None:
        return Path(platformdirs.user_data_dir(TOOL_NAME))

    # Fallback to platform-specific defaults
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    return base / TOOL_NAME


def generate_default_filename(command: str, timestamp: datetime | None = None) -> str:
    """Generate a timestamped default filename for exports.

    Args:
        command: The CLI command name (e.g., 'search', 'scrape_shops')
        timestamp: Optional timestamp to use (defaults to now)

    Returns:
        Generated filename with ISO 8601 compact timestamp.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    prefix = FILENAME_PREFIX_MAP.get(command, "export")
    ts_str = timestamp.strftime("%Y%m%dT%H%M%S")

    return f"{prefix}_{ts_str}.json"


def generate_export_metadata(
    entity_type: str,
    command: str,
    parameters: dict[str, Any],
    record_count: int,
    fields: list[dict[str, str]],
    execution_time_ms: int,
    source_urls: list[str],
    included_fields: list[str] | None = None,
    excluded_fields: list[str] | None = None,
) -> dict[str, Any]:
    """Generate export metadata structure.

    Args:
        entity_type: Type of data being exported (e.g., 'shops', 'search_results')
        command: CLI command that generated the data
        parameters: Parameters passed to the command
        record_count: Number of records in the data
        fields: List of field specifications
        execution_time_ms: Execution time in milliseconds
        source_urls: List of source URLs scraped
        included_fields: List of fields that were included in the export
        excluded_fields: List of fields that were excluded from the export

    Returns:
        Metadata dictionary.
    """
    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "entity_type": entity_type,
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_version": get_version(),
        "tool_name": TOOL_NAME,
        "record_count": record_count,
        "fields": fields,
        "lineage": {
            "command": command,
            "parameters": parameters,
            "source_urls": source_urls,
            "execution_time_ms": execution_time_ms,
            "field_filtering": {
                "included_fields": included_fields,
                "excluded_fields": excluded_fields,
            },
        },
        "validation_status": "passed",
    }


def ensure_directory_exists(path: Path) -> None:
    """Create parent directories for the given path if they don't exist.

    Args:
        path: The file path whose parent directories should be created

    Raises:
        OSError: If directory creation fails
    """
    parent = path.parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error("failed_to_create_directory", path=str(parent), error=str(e))
            raise OSError(f"Failed to create directory: {parent}") from e


def validate_output_path(path: str | Path) -> Path:
    """Validate and normalize the output path.

    This function:
    - Resolves tilde (~) to home directory
    - Resolves relative paths to absolute
    - Rejects path traversal attempts

    Args:
        path: The output path to validate

    Returns:
        Normalized absolute Path object

    Raises:
        ValueError: If path traversal is detected
    """
    # Convert to string if Path
    path_str = str(path)

    # Resolve tilde to home directory
    if path_str.startswith("~"):
        path_str = os.path.expanduser(path_str)

    # Create Path object and resolve to absolute
    path_obj = Path(path_str)
    if not path_obj.is_absolute():
        path_obj = path_obj.resolve()

    # Check for path traversal attempts
    # Check for explicit path traversal sequences in the original string
    # Normalize backslashes for cross-platform check
    traversal_patterns = [
        "..",
        "/../",
        "/..",
        "../",
        "..\\",
        "\\..\\",
        "\\..",
    ]
    for pattern in traversal_patterns:
        if pattern in path_str.replace("\\", "/"):
            raise ValueError("Invalid output path: path traversal not allowed")

    # Sanitize invalid filename characters
    # Remove or replace characters that are invalid on most filesystems
    filename = path_obj.name
    invalid_chars = r'[<>:"|?*\x00-\x1f]'
    if re.search(invalid_chars, filename):
        # Replace invalid characters with underscore
        sanitized = re.sub(invalid_chars, "_", filename)
        path_obj = path_obj.parent / sanitized

    return path_obj


def save_to_json(
    data: list[Any] | dict[str, Any],
    output_path: Path,
    metadata: dict[str, Any],
) -> None:
    """Save data with metadata to a JSON file.

    Args:
        data: The data to save (list or dict)
        output_path: Path where to save the JSON file
        metadata: Metadata to include with the data

    Raises:
        OSError: If file cannot be written (permission, disk full, etc.)
        ValueError: If data cannot be serialized
    """
    # Ensure parent directory exists
    ensure_directory_exists(output_path)

    # Prepare output structure
    output = {
        "metadata": metadata,
        "data": data,
    }

    # Serialize data using Pydantic models if available
    # This ensures proper JSON serialization of special types
    try:
        serialized_data = _serialize_for_json(data)
    except Exception as e:
        logger.error("serialization_failed", error=str(e))
        raise ValueError(f"Failed to serialize data: {e}") from e

    output["data"] = serialized_data

    # Write to file with pretty printing
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    except PermissionError as e:
        logger.error("permission_denied", path=str(output_path), error=str(e))
        raise OSError(f"Cannot write to {output_path}: permission denied") from e
    except OSError as e:
        if "No space left" in str(e) or e.errno == 28:
            logger.error("disk_full", path=str(output_path))
            raise OSError("Failed to save data: disk full") from e
        raise


def _serialize_for_json(data: Any) -> Any:
    """Serialize data for JSON output.

    Handles Pydantic models, datetime objects, and other special types.

    Args:
        data: The data to serialize

    Returns:
        JSON-serializable representation of the data
    """
    # Handle Pydantic models
    if hasattr(data, "model_dump"):
        return data.model_dump(mode="json")
    if hasattr(data, "dict"):
        # Pydantic v1 compatibility
        return data.dict()

    # Handle lists and tuples
    if isinstance(data, (list, tuple)):
        return [_serialize_for_json(item) for item in data]

    # Handle dictionaries
    if isinstance(data, dict):
        return {key: _serialize_for_json(value) for key, value in data.items()}

    # Handle datetime objects
    if isinstance(data, datetime):
        return data.isoformat()

    # Handle sets
    if isinstance(data, (set, frozenset)):
        return list(data)

    # Return as-is for primitives
    return data


def get_entity_fields(entity_type: str) -> list[dict[str, str]]:
    """Get field specifications for an entity type.

    Args:
        entity_type: The entity type (e.g., 'shops', 'search_results')

    Returns:
        List of field specifications with name, type, and description
    """
    field_specs: dict[str, list[dict[str, str]]] = {
        "shops": [
            {"name": "slug", "type": "string", "description": "URL slug for the shop"},
            {"name": "brand_id", "type": "integer", "description": "Blix brand ID"},
            {"name": "name", "type": "string", "description": "Shop name"},
            {"name": "logo_url", "type": "string", "description": "URL to shop logo"},
            {"name": "category", "type": "string", "description": "Shop category"},
            {"name": "leaflet_count", "type": "integer", "description": "Number of leaflets"},
            {"name": "is_popular", "type": "boolean", "description": "Whether shop is popular"},
            {"name": "scraped_at", "type": "datetime", "description": "Timestamp of scrape"},
        ],
        "search_results": [
            {"name": "hash", "type": "string", "description": "Unique hash identifier"},
            {"name": "name", "type": "string", "description": "Product name"},
            {"name": "image_url", "type": "string", "description": "Product image URL"},
            {"name": "price", "type": "decimal", "description": "Price in grosz"},
            {"name": "percent_discount", "type": "integer", "description": "Discount percentage"},
            {"name": "valid_from", "type": "datetime", "description": "Offer validity start"},
            {"name": "valid_until", "type": "datetime", "description": "Offer validity end"},
            {"name": "shop_name", "type": "string", "description": "Shop name"},
            {"name": "search_query", "type": "string", "description": "Search query"},
            {"name": "scraped_at", "type": "datetime", "description": "Timestamp of scrape"},
        ],
        "leaflets": [
            {"name": "leaflet_id", "type": "integer", "description": "Leaflet ID"},
            {"name": "shop_slug", "type": "string", "description": "Shop slug"},
            {"name": "name", "type": "string", "description": "Leaflet name"},
            {"name": "cover_image_url", "type": "string", "description": "Cover image URL"},
            {"name": "url", "type": "string", "description": "Leaflet URL"},
            {"name": "valid_from", "type": "datetime", "description": "Valid from date"},
            {"name": "valid_until", "type": "datetime", "description": "Valid until date"},
            {"name": "status", "type": "string", "description": "Leaflet status"},
            {"name": "page_count", "type": "integer", "description": "Number of pages"},
            {"name": "scraped_at", "type": "datetime", "description": "Timestamp of scrape"},
        ],
        "offers": [
            {"name": "leaflet_id", "type": "integer", "description": "Parent leaflet ID"},
            {"name": "name", "type": "string", "description": "Product name"},
            {"name": "price", "type": "decimal", "description": "Price in PLN"},
            {"name": "image_url", "type": "string", "description": "Product image URL"},
            {"name": "page_number", "type": "integer", "description": "Page number in leaflet"},
            {"name": "position_x", "type": "float", "description": "X position in leaflet"},
            {"name": "position_y", "type": "float", "description": "Y position in leaflet"},
            {"name": "width", "type": "float", "description": "Width in leaflet"},
            {"name": "height", "type": "float", "description": "Height in leaflet"},
            {"name": "valid_from", "type": "datetime", "description": "Valid from date"},
            {"name": "valid_until", "type": "datetime", "description": "Valid until date"},
            {"name": "scraped_at", "type": "datetime", "description": "Timestamp of scrape"},
        ],
        "full_shop": [
            {"name": "shop", "type": "object", "description": "Shop entity"},
            {"name": "leaflets", "type": "array", "description": "List of leaflets"},
            {"name": "offers", "type": "array", "description": "List of offers"},
            {"name": "keywords", "type": "array", "description": "List of keywords"},
        ],
    }

    return field_specs.get(entity_type, [])


# Entity type to class mapping for introspection
ENTITY_CLASS_MAP: dict[str, type] = {
    "shop": Shop,
    "leaflet": Leaflet,
    "offer": Offer,
    "search_result": SearchResult,
    "keyword": Keyword,
}


def get_available_fields(entity_type: str) -> list[str]:
    """Get available fields for an entity type using Pydantic model introspection.

    Args:
        entity_type: The entity type name (e.g., 'shop', 'leaflet', 'offer',
            'search_result', 'keyword')

    Returns:
        List of field names available for the entity

    Raises:
        ValueError: If entity_type is not supported
    """
    entity_class = ENTITY_CLASS_MAP.get(entity_type)
    if entity_class is None:
        valid_types = list(ENTITY_CLASS_MAP.keys())
        raise ValueError(f"Unknown entity type: '{entity_type}'. Valid types are: {valid_types}")

    return list(entity_class.model_fields.keys())


def validate_fields(entity_type: str, fields: list[str]) -> list[str]:
    """Validate field names against entity schema.

    Args:
        entity_type: The entity type name (e.g., 'shop', 'leaflet', 'offer',
            'search_result', 'keyword')
        fields: List of field names to validate

    Returns:
        List of valid field names (preserves original order of valid fields)

    Raises:
        ValueError: If any field is invalid, includes suggestions for close matches
    """
    available = get_available_fields(entity_type)
    available_set = set(available)

    invalid_fields: list[str] = []
    for field in fields:
        if field not in available_set:
            invalid_fields.append(field)

    if invalid_fields:
        error_parts: list[str] = []
        for invalid_field in invalid_fields:
            suggestion = get_field_suggestions(invalid_field, available)
            if suggestion:
                error_parts.append(f"'{invalid_field}' - {suggestion}")
            else:
                error_parts.append(f"'{invalid_field}' - unknown field")

        raise ValueError(
            f"Invalid fields for '{entity_type}': {', '.join(error_parts)}. "
            f"Use --fields-list {entity_type} to see available fields."
        )

    return fields


def filter_fields(
    data: dict[str, Any] | list[dict[str, Any]],
    fields: list[str] | None = None,
    exclude: list[str] | None = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Filter fields from data based on include/exclude lists.

    Order of operations: First include (if provided), then exclude (if provided).

    Args:
        data: Dictionary or list of dictionaries to filter
        fields: List of field names to include (if None, include all)
        exclude: List of field names to exclude (applied after include)

    Returns:
        Filtered data with only specified fields

    Raises:
        ValueError: If entity type cannot be inferred for nested data
    """
    # Handle list of dictionaries
    if isinstance(data, list):
        result_list: list[dict[str, Any]] = []
        for item in data:
            filtered_item = filter_fields(item, fields=fields, exclude=exclude)
            if isinstance(filtered_item, dict):
                result_list.append(filtered_item)
        return result_list

    # Handle dictionary
    if not isinstance(data, dict):
        return data

    result = data.copy()

    # First, apply include filter (if provided)
    if fields is not None:
        result = {k: v for k, v in result.items() if k in fields}

    # Then, apply exclude filter (if provided)
    if exclude is not None:
        result = {k: v for k, v in result.items() if k not in exclude}

    return result


def get_field_suggestions(invalid_field: str, valid_fields: list[str]) -> str | None:
    """Get fuzzy match suggestion for an invalid field name.

    Uses difflib to find close matches to help users correct typos.

    Args:
        invalid_field: The field name that wasn't recognized
        valid_fields: List of valid field names to match against

    Returns:
        Suggestion message like "Did you mean: 'name'?" or None if no close match
    """
    if not valid_fields:
        return None

    # Use difflib to find close matches (case-insensitive)
    matches = difflib.get_close_matches(
        invalid_field,
        valid_fields,
        n=1,
        cutoff=0.6,  # Require 60% similarity
    )

    if matches:
        return f"Did you mean: '{matches[0]}'?"

    # Try case-insensitive matching as fallback
    lower_valid = [f.lower() for f in valid_fields]
    lower_invalid = invalid_field.lower()

    # Check for exact case-insensitive match
    for i, lower_field in enumerate(lower_valid):
        if lower_field == lower_invalid:
            return f"Did you mean: '{valid_fields[i]}' (check case)?"

    return None
