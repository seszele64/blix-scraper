"""Tests for data export utilities."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from src.utils.data_export import (
    ensure_directory_exists,
    filter_fields,
    generate_default_filename,
    generate_export_metadata,
    get_available_fields,
    get_default_data_dir,
    get_entity_fields,
    get_field_suggestions,
    save_to_json,
    validate_fields,
    validate_output_path,
)


class TestGenerateDefaultFilename:
    """Tests for generate_default_filename function."""

    def test_generate_filename_with_timestamp(self):
        """Test filename generation with specific timestamp."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = generate_default_filename("search", timestamp)

        assert result == "search_results_20240115T143000.json"

    def test_generate_filename_default_timestamp(self):
        """Test filename generation with default (current) timestamp."""
        result = generate_default_filename("search")

        # Should match pattern search_results_YYYYMMDDTHHMMSS.json
        assert result.startswith("search_results_")
        assert result.endswith(".json")
        # Length should be: search_results_ (15) + YYYYMMDD (8) + T (1) + HHMMSS (6) + .json (5) = 35
        assert len(result) == 35

    def test_generate_filename_scrape_shops(self):
        """Test filename for scrape_shops command."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = generate_default_filename("scrape_shops", timestamp)

        assert result == "shops_20240115T143000.json"

    def test_generate_filename_scrape_leaflets(self):
        """Test filename for scrape_leaflets command."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = generate_default_filename("scrape_leaflets", timestamp)

        assert result == "leaflets_20240115T143000.json"

    def test_generate_filename_scrape_offers(self):
        """Test filename for scrape_offers command."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = generate_default_filename("scrape_offers", timestamp)

        assert result == "offers_20240115T143000.json"

    def test_generate_filename_scrape_full_shop(self):
        """Test filename for scrape_full_shop command."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = generate_default_filename("scrape_full_shop", timestamp)

        assert result == "full_shop_20240115T143000.json"

    def test_generate_filename_unknown_command(self):
        """Test filename for unknown command."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = generate_default_filename("unknown_command", timestamp)

        assert result == "export_20240115T143000.json"


class TestGenerateExportMetadata:
    """Tests for generate_export_metadata function."""

    def test_generate_metadata_basic(self):
        """Test basic metadata generation."""
        metadata = generate_export_metadata(
            entity_type="search_results",
            command="search",
            parameters={"query": "kawa"},
            record_count=10,
            fields=[{"name": "name", "type": "string"}],
            execution_time_ms=1500,
            source_urls=["https://blix.pl"],
        )

        assert metadata["schema_version"] == "1.0.0"
        assert metadata["entity_type"] == "search_results"
        assert metadata["tool_name"] == "blix-scraper"
        assert metadata["record_count"] == 10
        assert metadata["validation_status"] == "passed"
        assert "export_timestamp" in metadata
        assert metadata["lineage"]["command"] == "search"
        assert metadata["lineage"]["parameters"] == {"query": "kawa"}
        assert metadata["lineage"]["source_urls"] == ["https://blix.pl"]
        assert metadata["lineage"]["execution_time_ms"] == 1500


class TestEnsureDirectoryExists:
    """Tests for ensure_directory_exists function."""

    def test_create_directory(self, tmp_path):
        """Test creating a new directory."""
        test_dir = tmp_path / "new_dir" / "nested"
        ensure_directory_exists(test_dir / "file.json")

        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_existing_directory(self, tmp_path):
        """Test with existing directory."""
        test_dir = tmp_path / "existing"
        test_dir.mkdir()

        # Should not raise
        ensure_directory_exists(test_dir / "file.json")

        assert test_dir.exists()

    def test_create_directory_permissions_error(self, tmp_path):
        """Test handling of permission errors."""
        # Try to create directory in a protected location
        # This test may be skipped on some systems
        protected_path = Path("/root/test_dir_that_cannot_be_created")
        if os.access("/", os.W_OK):
            # Only run if we have write access to root (unlikely)
            with pytest.raises(OSError):
                ensure_directory_exists(protected_path / "file.json")


class TestValidateOutputPath:
    """Tests for validate_output_path function."""

    def test_simple_filename(self):
        """Test simple filename validation."""
        result = validate_output_path("output.json")

        assert result.is_absolute()
        assert result.name == "output.json"

    def test_tilde_expansion(self):
        """Test tilde expansion to home directory."""
        result = validate_output_path("~/test.json")

        assert result.is_absolute()
        assert result.name == "test.json"
        assert str(result).startswith(str(Path.home()))

    def test_relative_path_resolution(self):
        """Test relative path resolution."""
        result = validate_output_path("./test.json")

        assert result.is_absolute()
        assert result.name == "test.json"

    def test_nested_relative_path(self):
        """Test nested relative path."""
        result = validate_output_path("subdir/nested/file.json")

        assert result.is_absolute()
        assert result.name == "file.json"
        assert "subdir" in str(result)
        assert "nested" in str(result)

    def test_path_traversal_rejected(self):
        """Test that path traversal is rejected."""
        with pytest.raises(ValueError, match="path traversal not allowed"):
            validate_output_path("data/../../../etc/passwd")

    def test_path_traversal_with_dots(self):
        """Test path traversal with different patterns."""
        with pytest.raises(ValueError, match="path traversal not allowed"):
            validate_output_path("../secret.txt")

    def test_path_traversal_windows_style(self):
        """Test path traversal with Windows-style paths."""
        with pytest.raises(ValueError, match="path traversal not allowed"):
            validate_output_path("..\\..\\secret.txt")

    def test_sanitize_invalid_chars(self):
        """Test sanitization of invalid filename characters."""
        result = validate_output_path("file<name>?.json")

        # Should replace invalid characters
        assert "?" not in result.name
        assert "<" not in result.name
        assert ">" not in result.name

    def test_absolute_path_unchanged(self):
        """Test absolute path is unchanged."""
        abs_path = Path("/tmp/test.json")
        result = validate_output_path(abs_path)

        assert result == abs_path.resolve()


class TestSaveToJson:
    """Tests for save_to_json function."""

    def test_save_simple_data(self, tmp_path):
        """Test saving simple data."""
        data = [{"name": "test", "value": 123}]
        output_path = tmp_path / "output.json"
        metadata = {"record_count": 1}

        save_to_json(data, output_path, metadata)

        assert output_path.exists()

        with open(output_path) as f:
            result = json.load(f)

        assert "metadata" in result
        assert "data" in result
        assert result["data"] == data

    def test_save_with_complex_metadata(self, tmp_path):
        """Test saving with complex metadata."""
        data = [{"id": 1, "name": "Item"}]
        output_path = tmp_path / "complex.json"
        metadata = generate_export_metadata(
            entity_type="shops",
            command="scrape_shops",
            parameters={"headless": False},
            record_count=1,
            fields=get_entity_fields("shops"),
            execution_time_ms=100,
            source_urls=["https://blix.pl/sklepy/"],
        )

        save_to_json(data, output_path, metadata)

        with open(output_path) as f:
            result = json.load(f)

        assert result["metadata"]["entity_type"] == "shops"
        assert result["metadata"]["record_count"] == 1

    def test_save_to_nested_directory(self, tmp_path):
        """Test saving to nested directory that doesn't exist."""
        data = [1, 2, 3]
        output_path = tmp_path / "nested" / "dirs" / "output.json"
        metadata = {"record_count": 3}

        save_to_json(data, output_path, metadata)

        assert output_path.exists()

    def test_save_empty_list(self, tmp_path):
        """Test saving empty list."""
        data = []
        output_path = tmp_path / "empty.json"
        metadata = {"record_count": 0}

        save_to_json(data, output_path, metadata)

        with open(output_path) as f:
            result = json.load(f)

        assert result["data"] == []

    def test_save_dict_data(self, tmp_path):
        """Test saving dictionary data (for full_shop export)."""
        data = {
            "shop": {"name": "Test Shop"},
            "leaflets": [{"id": 1}],
            "offers": [],
            "keywords": [],
        }
        output_path = tmp_path / "dict_data.json"
        metadata = {"record_count": 1}

        save_to_json(data, output_path, metadata)

        with open(output_path) as f:
            result = json.load(f)

        assert result["data"]["shop"]["name"] == "Test Shop"

    def test_save_permission_denied(self):
        """Test handling of permission denied error."""
        # This test would require a protected directory
        # Skipping for most test environments
        pytest.skip("Requires protected directory")


class TestGetEntityFields:
    """Tests for get_entity_fields function."""

    def test_get_fields_shops(self):
        """Test getting fields for shops."""
        fields = get_entity_fields("shops")

        assert len(fields) > 0
        assert any(f["name"] == "slug" for f in fields)
        assert any(f["name"] == "name" for f in fields)

    def test_get_fields_search_results(self):
        """Test getting fields for search_results."""
        fields = get_entity_fields("search_results")

        assert len(fields) > 0
        assert any(f["name"] == "name" for f in fields)
        assert any(f["name"] == "price" for f in fields)

    def test_get_fields_leaflets(self):
        """Test getting fields for leaflets."""
        fields = get_entity_fields("leaflets")

        assert len(fields) > 0
        assert any(f["name"] == "leaflet_id" for f in fields)

    def test_get_fields_offers(self):
        """Test getting fields for offers."""
        fields = get_entity_fields("offers")

        assert len(fields) > 0
        assert any(f["name"] == "price" for f in fields)

    def test_get_fields_full_shop(self):
        """Test getting fields for full_shop."""
        fields = get_entity_fields("full_shop")

        assert len(fields) > 0
        assert any(f["name"] == "shop" for f in fields)
        assert any(f["name"] == "leaflets" for f in fields)

    def test_get_fields_unknown(self):
        """Test getting fields for unknown entity type."""
        fields = get_entity_fields("unknown_type")

        assert fields == []


class TestGetDefaultDataDir:
    """Tests for get_default_data_dir function."""

    def test_returns_path(self):
        """Test that it returns a Path object."""
        result = get_default_data_dir()

        assert isinstance(result, Path)
        assert "blix-scraper" in str(result)

    def test_is_absolute(self):
        """Test that returned path is absolute."""
        result = get_default_data_dir()

        assert result.is_absolute()


class TestFieldFiltering:
    """Tests for field filtering utility functions."""

    # Tests for get_available_fields()

    def test_get_available_fields_shop(self):
        """Test getting available fields for shop entity."""
        fields = get_available_fields("shop")

        assert "name" in fields
        assert "slug" in fields
        assert "brand_id" in fields
        assert "logo_url" in fields
        assert "category" in fields
        assert "leaflet_count" in fields
        assert "is_popular" in fields
        assert "scraped_at" in fields

    def test_get_available_fields_leaflet(self):
        """Test getting available fields for leaflet entity."""
        fields = get_available_fields("leaflet")

        assert "leaflet_id" in fields
        assert "shop_slug" in fields
        assert "name" in fields
        assert "cover_image_url" in fields
        assert "url" in fields
        assert "valid_from" in fields
        assert "valid_until" in fields
        assert "status" in fields
        assert "page_count" in fields
        assert "scraped_at" in fields

    def test_get_available_fields_offer(self):
        """Test getting available fields for offer entity."""
        fields = get_available_fields("offer")

        assert "leaflet_id" in fields
        assert "name" in fields
        assert "price" in fields
        assert "image_url" in fields
        assert "page_number" in fields
        assert "position_x" in fields
        assert "position_y" in fields
        assert "width" in fields
        assert "height" in fields
        assert "valid_from" in fields
        assert "valid_until" in fields
        assert "scraped_at" in fields

    def test_get_available_fields_search_result(self):
        """Test getting available fields for search_result entity."""
        fields = get_available_fields("search_result")

        assert "hash" in fields
        assert "name" in fields
        assert "image_url" in fields
        assert "price" in fields
        assert "percent_discount" in fields
        assert "valid_from" in fields
        assert "valid_until" in fields
        assert "shop_name" in fields
        assert "search_query" in fields
        assert "scraped_at" in fields

    def test_get_available_fields_keyword(self):
        """Test getting available fields for keyword entity."""
        fields = get_available_fields("keyword")

        assert "leaflet_id" in fields
        assert "text" in fields
        assert "url" in fields
        assert "category_path" in fields
        assert "scraped_at" in fields

    def test_get_available_fields_unknown_entity(self):
        """Test getting fields for unknown entity type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown entity type"):
            get_available_fields("unknown_entity")

    # Tests for validate_fields()

    def test_validate_fields_valid_fields(self):
        """Test that valid fields pass validation."""
        result = validate_fields("shop", ["name", "slug", "brand_id"])

        assert result == ["name", "slug", "brand_id"]

    def test_validate_fields_single_valid_field(self):
        """Test validation with a single valid field."""
        result = validate_fields("leaflet", ["name"])

        assert result == ["name"]

    def test_validate_fields_empty_list(self):
        """Test validation with empty list returns empty list."""
        result = validate_fields("shop", [])

        assert result == []

    def test_validate_fields_invalid_field_raises_error(self):
        """Test that invalid field raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_fields("shop", ["name", "invalid_field"])

        assert "Invalid fields for 'shop'" in str(exc_info.value)

    def test_validate_fields_invalid_field_with_suggestion(self):
        """Test that invalid field with typo provides suggestion."""
        with pytest.raises(ValueError) as exc_info:
            validate_fields("shop", ["nme"])

        assert "Did you mean: 'name'?" in str(exc_info.value)

    def test_validate_fields_multiple_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        with pytest.raises(ValueError) as exc_info:
            validate_fields("shop", ["nme", "slg", "brand_idd"])

        # Should have suggestions for close matches
        error_msg = str(exc_info.value)
        assert "Did you mean: 'name'?" in error_msg or "Did you mean: 'slug'?" in error_msg

    def test_validate_fields_all_invalid(self):
        """Test validation when all fields are invalid."""
        with pytest.raises(ValueError) as exc_info:
            validate_fields("offer", ["invalid1", "invalid2"])

        assert "Invalid fields for 'offer'" in str(exc_info.value)

    # Tests for filter_fields()

    def test_filter_fields_include_only(self):
        """Test filtering to include only specified fields."""
        data = {"name": "Test", "slug": "test", "brand_id": 123, "category": "Food"}

        result = filter_fields(data, fields=["name", "slug"])

        assert result == {"name": "Test", "slug": "test"}
        assert "brand_id" not in result
        assert "category" not in result

    def test_filter_fields_exclude_only(self):
        """Test filtering to exclude specified fields."""
        data = {"name": "Test", "slug": "test", "brand_id": 123, "category": "Food"}

        result = filter_fields(data, exclude=["brand_id", "category"])

        assert result == {"name": "Test", "slug": "test"}
        assert "brand_id" not in result
        assert "category" not in result

    def test_filter_fields_include_then_exclude(self):
        """Test that include is applied first, then exclude."""
        data = {"name": "Test", "slug": "test", "logo_url": "http://test.jpg", "category": "Food"}

        result = filter_fields(data, fields=["name", "slug", "logo_url"], exclude=["logo_url"])

        # Should include name and slug but exclude logo_url
        assert result == {"name": "Test", "slug": "test"}
        assert "logo_url" not in result
        assert "category" not in result

    def test_filter_fields_list_of_dicts(self):
        """Test filtering a list of dictionaries."""
        data = [
            {"name": "Test1", "slug": "test1", "brand_id": 1},
            {"name": "Test2", "slug": "test2", "brand_id": 2},
        ]

        result = filter_fields(data, fields=["name"])

        assert len(result) == 2
        assert result[0] == {"name": "Test1"}
        assert result[1] == {"name": "Test2"}

    def test_filter_fields_list_exclude(self):
        """Test excluding fields from a list of dictionaries."""
        data = [
            {"name": "Test1", "slug": "test1", "category": "Food"},
            {"name": "Test2", "slug": "test2", "category": "Electronics"},
        ]

        result = filter_fields(data, exclude=["category"])

        assert len(result) == 2
        assert "category" not in result[0]
        assert "category" not in result[1]
        assert result[0]["name"] == "Test1"

    def test_filter_fields_no_filter(self):
        """Test that no filtering is applied when both params are None."""
        data = {"name": "Test", "slug": "test", "brand_id": 123}

        result = filter_fields(data)

        assert result == data

    def test_filter_fields_non_dict_returns_original(self):
        """Test that non-dict data returns unchanged."""
        # Test with integer as non-dict input
        result = filter_fields(42, fields=["name"])

        assert result == 42

    def test_filter_fields_empty_dict(self):
        """Test filtering empty dictionary."""
        result = filter_fields({}, fields=["name"])

        assert result == {}

    def test_filter_fields_nested_data(self):
        """Test filtering with nested dictionary data."""
        data: dict[str, Any] = {
            "shop": {"name": "Test Shop", "slug": "test", "brand_id": 123},
            "leaflets": [{"name": "Leaflet1"}],
        }

        result = filter_fields(data, fields=["shop"])

        assert result == {"shop": {"name": "Test Shop", "slug": "test", "brand_id": 123}}

    # Tests for get_field_suggestions()

    def test_get_field_suggestions_close_match(self):
        """Test getting suggestion for close match."""
        valid_fields = ["name", "slug", "brand_id", "category"]

        suggestion = get_field_suggestions("nme", valid_fields)

        assert suggestion is not None
        assert "name" in suggestion

    def test_get_field_suggestions_no_match(self):
        """Test no suggestion for far-off field name."""
        valid_fields = ["name", "slug", "brand_id"]

        suggestion = get_field_suggestions("xyz123", valid_fields)

        assert suggestion is None

    def test_get_field_suggestions_case_difference(self):
        """Test suggestion for case difference."""
        valid_fields = ["name", "slug"]

        suggestion = get_field_suggestions("NAME", valid_fields)

        assert suggestion is not None
        assert "name" in suggestion.lower()

    def test_get_field_suggestions_empty_valid_fields(self):
        """Test no suggestion when valid fields list is empty."""
        suggestion = get_field_suggestions("test", [])

        assert suggestion is None

    def test_get_field_suggestions_exact_match(self):
        """Test suggestion for exact match."""
        valid_fields = ["name", "slug"]

        suggestion = get_field_suggestions("name", valid_fields)

        # get_close_matches returns the exact match at high similarity
        assert suggestion is not None
        assert "name" in suggestion

    def test_get_field_suggestions_partial_match(self):
        """Test suggestion for partial match."""
        valid_fields = ["category", "leaflet_count", "brand_id"]

        suggestion = get_field_suggestions("categor", valid_fields)

        assert suggestion is not None
        assert "category" in suggestion
