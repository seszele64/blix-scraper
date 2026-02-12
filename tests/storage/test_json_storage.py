"""Tests for JSON storage."""

import json
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import HttpUrl

from src.domain.entities import Leaflet, Offer, Shop
from src.storage.field_filter import FieldFilter
from src.storage.json_storage import JSONStorage


@pytest.fixture
def shop_storage(tmp_path):
    """Create shop storage instance with tmp_path."""
    return JSONStorage(tmp_path, Shop)


@pytest.fixture
def leaflet_storage(tmp_path):
    """Create leaflet storage instance with tmp_path."""
    return JSONStorage(tmp_path, Leaflet)


@pytest.fixture
def offer_storage(tmp_path):
    """Create offer storage instance with tmp_path."""
    return JSONStorage(tmp_path, Offer)


@pytest.fixture
def sample_shop_dict():
    """Sample shop data as dictionary."""
    return {
        "slug": "biedronka",
        "brand_id": 23,
        "name": "Biedronka",
        "logo_url": "https://img.blix.pl/image/brand/thumbnail_23.jpg",
        "category": "Sklepy spożywcze",
        "leaflet_count": 13,
        "is_popular": True,
        "scraped_at": "2025-10-30T12:00:00Z",
    }


@pytest.fixture
def sample_leaflet_dict():
    """Sample leaflet data as dictionary."""
    return {
        "leaflet_id": 457727,
        "shop_slug": "biedronka",
        "name": "Od środy",
        "cover_image_url": "https://imgproxy.blix.pl/image/leaflet/457727/cover.jpg",
        "url": "https://blix.pl/sklep/biedronka/gazetka/457727/",
        "valid_from": "2025-10-29T00:00:00Z",
        "valid_until": "2025-11-05T23:59:59Z",
        "status": "active",
        "page_count": 12,
        "scraped_at": "2025-10-30T12:05:00Z",
    }


@pytest.mark.unit
class TestJSONStorageInitialization:
    """Tests for JSONStorage initialization."""

    def test_initialization_creates_directory(self, tmp_path):
        """Test that initialization creates base directory."""
        storage_dir = tmp_path / "storage"
        storage = JSONStorage(storage_dir, Shop)

        assert storage.base_dir == storage_dir
        assert storage.entity_type == Shop
        assert storage_dir.exists()
        assert storage_dir.is_dir()

    def test_initialization_with_existing_directory(self, tmp_path):
        """Test initialization with existing directory."""
        storage_dir = tmp_path / "existing"
        storage_dir.mkdir()

        storage = JSONStorage(storage_dir, Shop)

        assert storage.base_dir == storage_dir
        assert storage_dir.exists()

    def test_initialization_with_nested_path(self, tmp_path):
        """Test initialization creates nested directories."""
        storage_dir = tmp_path / "deep" / "nested" / "path"
        JSONStorage(storage_dir, Shop)

        assert storage_dir.exists()
        assert storage_dir.is_dir()


@pytest.mark.unit
class TestJSONStorageSave:
    """Tests for JSONStorage save operations."""

    def test_save_entity_creates_file(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving entity creates JSON file."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)

        # Act
        filepath = shop_storage.save(shop, "biedronka.json")

        # Assert
        assert filepath == tmp_path / "biedronka.json"
        assert filepath.exists()
        assert filepath.is_file()

    def test_save_entity_content(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving entity writes correct JSON content."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)

        # Act
        shop_storage.save(shop, "biedronka.json")

        # Assert
        with open(tmp_path / "biedronka.json", encoding="utf-8") as f:
            data = json.load(f)

        assert data["slug"] == "biedronka"
        assert data["name"] == "Biedronka"
        assert data["brand_id"] == 23
        assert data["logo_url"] == "https://img.blix.pl/image/brand/thumbnail_23.jpg"
        assert data["category"] == "Sklepy spożywcze"
        assert data["leaflet_count"] == 13
        assert data["is_popular"] is True

    def test_save_entity_with_datetime(self, leaflet_storage, sample_leaflet_dict, tmp_path):
        """Test saving entity with datetime fields."""
        # Arrange
        leaflet = Leaflet.model_validate(sample_leaflet_dict)

        # Act
        leaflet_storage.save(leaflet, "leaflet.json")

        # Assert
        with open(tmp_path / "leaflet.json", encoding="utf-8") as f:
            data = json.load(f)

        assert data["leaflet_id"] == 457727
        assert data["shop_slug"] == "biedronka"
        assert "valid_from" in data
        assert "valid_until" in data
        assert data["status"] == "active"

    def test_save_entity_with_decimal(self, offer_storage, tmp_path):
        """Test saving entity with Decimal fields."""
        # Arrange
        offer = Offer(
            leaflet_id=457727,
            name="Test Product",
            price=Decimal("12.99"),
            image_url=HttpUrl("https://example.com/image.jpg"),
            page_number=1,
            position_x=0.5,
            position_y=0.5,
            width=0.2,
            height=0.2,
            valid_from=datetime.now(timezone.utc),
            valid_until=datetime.now(timezone.utc),
        )

        # Act
        offer_storage.save(offer, "offer.json")

        # Assert
        with open(tmp_path / "offer.json", encoding="utf-8") as f:
            data = json.load(f)

        assert data["price"] == "12.99"  # Decimal serialized as string

    def test_save_entity_overwrites_existing(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving entity overwrites existing file."""
        # Arrange
        shop1 = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop1, "shop.json")

        sample_shop_dict["name"] = "Updated Name"
        shop2 = Shop.model_validate(sample_shop_dict)

        # Act
        shop_storage.save(shop2, "shop.json")

        # Assert
        with open(tmp_path / "shop.json", encoding="utf-8") as f:
            data = json.load(f)

        assert data["name"] == "Updated Name"

    def test_save_many_entities(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving multiple entities to single file."""
        # Arrange
        shop1 = Shop.model_validate(sample_shop_dict)

        sample_shop_dict["slug"] = "lidl"
        sample_shop_dict["name"] = "Lidl"
        shop2 = Shop.model_validate(sample_shop_dict)

        shops = [shop1, shop2]

        # Act
        filepath = shop_storage.save_many(shops, "all_shops.json")

        # Assert
        assert filepath == tmp_path / "all_shops.json"
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["slug"] == "biedronka"
        assert data[1]["slug"] == "lidl"

    def test_save_many_empty_list(self, shop_storage, tmp_path):
        """Test saving empty list creates file with empty array."""
        # Act
        filepath = shop_storage.save_many([], "empty.json")

        # Assert
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        assert data == []

    def test_save_with_field_filter(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving entity with field filter."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        field_filter = FieldFilter.custom("slug", "name", "category")

        # Act
        shop_storage.save(shop, "filtered.json", field_filter=field_filter)

        # Assert
        with open(tmp_path / "filtered.json", encoding="utf-8") as f:
            data = json.load(f)

        assert set(data.keys()) == {"slug", "name", "category"}
        assert data["slug"] == "biedronka"
        assert data["name"] == "Biedronka"
        assert "brand_id" not in data

    def test_save_many_with_field_filter(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving multiple entities with field filter."""
        # Arrange
        shop1 = Shop.model_validate(sample_shop_dict)

        sample_shop_dict["slug"] = "lidl"
        sample_shop_dict["name"] = "Lidl"
        shop2 = Shop.model_validate(sample_shop_dict)

        shops = [shop1, shop2]
        field_filter = FieldFilter.custom("slug", "name")

        # Act
        shop_storage.save_many(shops, "filtered_many.json", field_filter=field_filter)

        # Assert
        with open(tmp_path / "filtered_many.json", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2
        assert set(data[0].keys()) == {"slug", "name"}
        assert set(data[1].keys()) == {"slug", "name"}


@pytest.mark.unit
class TestJSONStorageLoad:
    """Tests for JSONStorage load operations."""

    def test_load_entity(self, shop_storage, sample_shop_dict):
        """Test loading entity from JSON file."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop, "biedronka.json")

        # Act
        loaded_shop = shop_storage.load("biedronka.json")

        # Assert
        assert loaded_shop is not None
        assert loaded_shop.slug == "biedronka"
        assert loaded_shop.name == "Biedronka"
        assert loaded_shop.brand_id == 23
        assert isinstance(loaded_shop, Shop)

    def test_load_nonexistent_file(self, shop_storage):
        """Test loading non-existent file returns None."""
        # Act
        result = shop_storage.load("nonexistent.json")

        # Assert
        assert result is None

    def test_load_invalid_json(self, shop_storage, tmp_path):
        """Test loading file with invalid JSON returns None."""
        # Arrange
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }", encoding="utf-8")

        # Act
        result = shop_storage.load("invalid.json")

        # Assert
        assert result is None

    def test_load_with_validation_error(self, shop_storage, tmp_path):
        """Test loading file with invalid data returns None."""
        # Arrange
        invalid_file = tmp_path / "invalid_data.json"
        invalid_file.write_text('{"slug": "test"}', encoding="utf-8")  # Missing required fields

        # Act
        result = shop_storage.load("invalid_data.json")

        # Assert
        assert result is None

    def test_load_all_empty_directory(self, shop_storage):
        """Test loading all entities from empty directory."""
        # Act
        entities = shop_storage.load_all()

        # Assert
        assert entities == []

    def test_load_all_multiple_files(self, shop_storage, sample_shop_dict):
        """Test loading all entities from directory with multiple files."""
        # Arrange
        shop1 = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop1, "biedronka.json")

        sample_shop_dict["slug"] = "lidl"
        sample_shop_dict["name"] = "Lidl"
        shop2 = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop2, "lidl.json")

        sample_shop_dict["slug"] = "kaufland"
        sample_shop_dict["name"] = "Kaufland"
        shop3 = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop3, "kaufland.json")

        # Act
        shops = shop_storage.load_all()

        # Assert
        assert len(shops) == 3
        slugs = {s.slug for s in shops}
        assert slugs == {"biedronka", "lidl", "kaufland"}

    def test_load_all_ignores_non_json_files(self, shop_storage, sample_shop_dict, tmp_path):
        """Test load_all ignores non-JSON files."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop, "biedronka.json")

        # Create non-JSON files
        (tmp_path / "readme.txt").write_text("test", encoding="utf-8")
        (tmp_path / "data.csv").write_text("a,b,c", encoding="utf-8")

        # Act
        shops = shop_storage.load_all()

        # Assert
        assert len(shops) == 1
        assert shops[0].slug == "biedronka"

    def test_load_all_skips_invalid_files(self, shop_storage, sample_shop_dict, tmp_path):
        """Test load_all skips files that fail to load."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop, "valid.json")

        # Create invalid JSON file
        (tmp_path / "invalid.json").write_text("{ invalid }", encoding="utf-8")

        # Act
        shops = shop_storage.load_all()

        # Assert
        assert len(shops) == 1
        assert shops[0].slug == "biedronka"


@pytest.mark.unit
class TestJSONStorageExists:
    """Tests for JSONStorage exists method."""

    def test_exists_true(self, shop_storage, sample_shop_dict):
        """Test exists returns True for existing file."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop, "biedronka.json")

        # Act
        result = shop_storage.exists("biedronka.json")

        # Assert
        assert result is True

    def test_exists_false(self, shop_storage):
        """Test exists returns False for non-existent file."""
        # Act
        result = shop_storage.exists("nonexistent.json")

        # Assert
        assert result is False


@pytest.mark.unit
class TestJSONStorageErrorHandling:
    """Tests for JSONStorage error handling."""

    def test_save_permission_error(self, sample_shop_dict, tmp_path):
        """Test save handles permission errors gracefully."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only directory

        # Act & Assert
        with pytest.raises(PermissionError):
            JSONStorage(readonly_dir, Shop).save(shop, "test.json")

        # Cleanup
        readonly_dir.chmod(0o755)

    def test_load_permission_error(self, shop_storage, tmp_path):
        """Test load handles permission errors gracefully."""
        # Arrange
        readonly_file = tmp_path / "readonly.json"
        readonly_file.write_text('{"test": "data"}', encoding="utf-8")
        readonly_file.chmod(0o000)  # No permissions

        # Act
        result = shop_storage.load("readonly.json")

        # Assert
        assert result is None

        # Cleanup
        readonly_file.chmod(0o644)


@pytest.mark.unit
class TestJSONStorageFieldFilterIntegration:
    """Tests for FieldFilter integration with JSONStorage."""

    def test_save_with_base_filter(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving with base field filter."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        field_filter = FieldFilter.with_dates()

        # Act
        shop_storage.save(shop, "base_filtered.json", field_filter=field_filter)

        # Assert
        with open(tmp_path / "base_filtered.json", encoding="utf-8") as f:
            data = json.load(f)

        # Base schema includes name, price, valid_from, valid_until
        # Shop doesn't have price, so should have name
        assert "name" in data

    def test_save_with_minimal_filter(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving with minimal field filter."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        field_filter = FieldFilter.minimal()

        # Act
        shop_storage.save(shop, "minimal_filtered.json", field_filter=field_filter)

        # Assert
        with open(tmp_path / "minimal_filtered.json", encoding="utf-8") as f:
            data = json.load(f)

        # Minimal includes name, price, shop_name
        assert "name" in data
        assert len(data) <= 3

    def test_save_with_extended_filter(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving with extended field filter."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)
        field_filter = FieldFilter.extended("brand_id", "logo_url")

        # Act
        shop_storage.save(shop, "extended_filtered.json", field_filter=field_filter)

        # Assert
        with open(tmp_path / "extended_filtered.json", encoding="utf-8") as f:
            data = json.load(f)

        # Should have base fields plus extended fields
        assert "name" in data
        assert "brand_id" in data
        assert "logo_url" in data

    def test_save_many_with_filter(self, shop_storage, sample_shop_dict, tmp_path):
        """Test saving many entities with field filter."""
        # Arrange
        shops = [
            Shop.model_validate(sample_shop_dict),
            Shop.model_validate({**sample_shop_dict, "slug": "lidl", "name": "Lidl"}),
        ]
        field_filter = FieldFilter.custom("slug", "name")

        # Act
        shop_storage.save_many(shops, "filtered_many.json", field_filter=field_filter)

        # Assert
        with open(tmp_path / "filtered_many.json", encoding="utf-8") as f:
            data = json.load(f)

        assert all(set(item.keys()) == {"slug", "name"} for item in data)


@pytest.mark.unit
class TestJSONStoragePydanticModels:
    """Tests for JSONStorage with various Pydantic models."""

    def test_save_and_load_shop(self, shop_storage, sample_shop_dict):
        """Test save and load roundtrip for Shop model."""
        # Arrange
        original_shop = Shop.model_validate(sample_shop_dict)

        # Act
        shop_storage.save(original_shop, "shop.json")
        loaded_shop = shop_storage.load("shop.json")

        # Assert
        assert loaded_shop is not None
        assert loaded_shop == original_shop
        assert isinstance(loaded_shop, Shop)

    def test_save_and_load_leaflet(self, leaflet_storage, sample_leaflet_dict):
        """Test save and load roundtrip for Leaflet model."""
        # Arrange
        original_leaflet = Leaflet.model_validate(sample_leaflet_dict)

        # Act
        leaflet_storage.save(original_leaflet, "leaflet.json")
        loaded_leaflet = leaflet_storage.load("leaflet.json")

        # Assert
        assert loaded_leaflet is not None
        assert loaded_leaflet == original_leaflet
        assert isinstance(loaded_leaflet, Leaflet)

    def test_save_and_load_offer(self, offer_storage):
        """Test save and load roundtrip for Offer model."""
        # Arrange
        original_offer = Offer(
            leaflet_id=457727,
            name="Test Product",
            price=Decimal("12.99"),
            image_url=HttpUrl("https://example.com/image.jpg"),
            page_number=1,
            position_x=0.5,
            position_y=0.5,
            width=0.2,
            height=0.2,
            valid_from=datetime.now(timezone.utc),
            valid_until=datetime.now(timezone.utc),
        )

        # Act
        offer_storage.save(original_offer, "offer.json")
        loaded_offer = offer_storage.load("offer.json")

        # Assert
        assert loaded_offer is not None
        assert loaded_offer.name == original_offer.name
        assert loaded_offer.price == original_offer.price
        assert isinstance(loaded_offer, Offer)
