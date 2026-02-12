"""Comprehensive unit tests for domain entities.

Tests cover all Pydantic models in src/domain/entities.py including:
- Shop: Retail brand entity
- LeafletStatus: Enum for leaflet status
- Leaflet: Promotional leaflet entity
- Offer: Product offer within leaflet
- SearchResult: Search result from search engine
- Keyword: Product keyword/category tag
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.domain.entities import (
    Keyword,
    Leaflet,
    LeafletStatus,
    Offer,
    SearchResult,
    Shop,
)


@pytest.mark.unit
class TestShop:
    """Comprehensive tests for Shop entity."""

    # ========== Valid Creation Tests ==========

    def test_create_shop_with_all_fields(self, sample_shop_dict):
        """Test creating shop with all fields populated."""
        # Arrange
        shop_data = sample_shop_dict.copy()

        # Act
        shop = Shop.model_validate(shop_data)

        # Assert
        assert shop.slug == "biedronka"
        assert shop.brand_id == 23
        assert shop.name == "Biedronka"
        assert str(shop.logo_url) == "https://img.blix.pl/image/brand/thumbnail_23.jpg"
        assert shop.category == "Sklepy spożywcze"
        assert shop.leaflet_count == 13
        assert shop.is_popular is True

    def test_create_shop_minimal_fields(self):
        """Test creating shop with only required fields."""
        # Arrange
        shop_data = {
            "slug": "kaufland",
            "name": "Kaufland",
            "logo_url": "https://example.com/logo.jpg",
            "leaflet_count": 0,
        }

        # Act
        shop = Shop.model_validate(shop_data)

        # Assert
        assert shop.slug == "kaufland"
        assert shop.name == "Kaufland"
        assert shop.brand_id is None
        assert shop.category is None
        assert shop.leaflet_count == 0
        assert shop.is_popular is False

    def test_shop_scraped_at_default(self):
        """Test that scraped_at defaults to current UTC time."""
        # Arrange
        shop_data = {
            "slug": "test",
            "name": "Test Shop",
            "logo_url": "https://example.com/logo.jpg",
            "leaflet_count": 0,
        }

        # Act
        before = datetime.now(timezone.utc)
        shop = Shop.model_validate(shop_data)
        after = datetime.now(timezone.utc)

        # Assert
        assert before <= shop.scraped_at <= after
        assert shop.scraped_at.tzinfo == timezone.utc

    # ========== Validation Tests ==========

    @pytest.mark.parametrize(
        "slug,should_fail",
        [
            ("valid-slug", False),
            ("valid_slug_123", False),
            ("UPPERCASE", False),
            ("   ", False),  # Whitespace is valid (length > 0)
            ("", True),  # Empty string
        ],
    )
    def test_shop_slug_validation(self, slug, should_fail, sample_shop_dict):
        """Test shop slug validation (min_length=1)."""
        # Arrange
        shop_data = sample_shop_dict.copy()
        shop_data["slug"] = slug

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                Shop.model_validate(shop_data)
            assert "slug" in str(exc_info.value).lower()
        else:
            shop = Shop.model_validate(shop_data)
            assert shop.slug == slug

    @pytest.mark.parametrize(
        "name,should_fail",
        [
            ("Valid Name", False),
            ("Shop-123", False),
            ("   ", False),  # Whitespace is valid (length > 0)
            ("", True),  # Empty string
        ],
    )
    def test_shop_name_validation(self, name, should_fail, sample_shop_dict):
        """Test shop name validation (min_length=1)."""
        # Arrange
        shop_data = sample_shop_dict.copy()
        shop_data["name"] = name

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                Shop.model_validate(shop_data)
            assert "name" in str(exc_info.value).lower()
        else:
            shop = Shop.model_validate(shop_data)
            assert shop.name == name

    @pytest.mark.parametrize(
        "logo_url,should_fail",
        [
            ("https://example.com/logo.jpg", False),
            ("http://example.com/logo.png", False),
            ("https://cdn.example.com/path/to/image.svg", False),
            ("not-a-url", True),
            ("ftp://example.com/logo.jpg", True),  # Not http/https
            ("", True),
            (None, True),
        ],
    )
    def test_shop_logo_url_validation(self, logo_url, should_fail, sample_shop_dict):
        """Test shop logo URL validation (HttpUrl type)."""
        # Arrange
        shop_data = sample_shop_dict.copy()
        shop_data["logo_url"] = logo_url

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError):
                Shop.model_validate(shop_data)
        else:
            shop = Shop.model_validate(shop_data)
            assert str(shop.logo_url) == logo_url

    @pytest.mark.parametrize(
        "leaflet_count,should_fail",
        [
            (0, False),
            (1, False),
            (100, False),
            (-1, True),
            (-100, True),
        ],
    )
    def test_shop_leaflet_count_validation(self, leaflet_count, should_fail, sample_shop_dict):
        """Test shop leaflet count validation (ge=0)."""
        # Arrange
        shop_data = sample_shop_dict.copy()
        shop_data["leaflet_count"] = leaflet_count

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                Shop.model_validate(shop_data)
            assert "leaflet_count" in str(exc_info.value).lower()
        else:
            shop = Shop.model_validate(shop_data)
            assert shop.leaflet_count == leaflet_count

    @pytest.mark.parametrize(
        "brand_id,should_be_none",
        [
            (23, False),
            (0, False),
            (None, True),
        ],
    )
    def test_shop_brand_id_optional(self, brand_id, should_be_none, sample_shop_dict):
        """Test shop brand_id is optional."""
        # Arrange
        shop_data = sample_shop_dict.copy()
        shop_data["brand_id"] = brand_id

        # Act
        shop = Shop.model_validate(shop_data)

        # Assert
        if should_be_none:
            assert shop.brand_id is None
        else:
            assert shop.brand_id == brand_id

    @pytest.mark.parametrize(
        "category,should_be_none",
        [
            ("Sklepy spożywcze", False),
            ("", False),  # Empty string is valid for optional str
            (None, True),
        ],
    )
    def test_shop_category_optional(self, category, should_be_none, sample_shop_dict):
        """Test shop category is optional."""
        # Arrange
        shop_data = sample_shop_dict.copy()
        shop_data["category"] = category

        # Act
        shop = Shop.model_validate(shop_data)

        # Assert
        if should_be_none:
            assert shop.category is None
        else:
            assert shop.category == category

    # ========== Serialization Tests ==========

    def test_shop_model_dump(self, sample_shop_dict):
        """Test Shop serialization to dictionary."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)

        # Act
        dumped = shop.model_dump()

        # Assert
        assert isinstance(dumped, dict)
        assert dumped["slug"] == "biedronka"
        assert dumped["name"] == "Biedronka"
        assert dumped["is_popular"] is True

    def test_shop_model_dump_json(self, sample_shop_dict):
        """Test Shop serialization to JSON string."""
        # Arrange
        shop = Shop.model_validate(sample_shop_dict)

        # Act
        json_str = shop.model_dump_json()

        # Assert
        assert isinstance(json_str, str)
        assert "biedronka" in json_str
        assert "Biedronka" in json_str

    def test_shop_model_validate_roundtrip(self, sample_shop_dict):
        """Test Shop serialization and deserialization roundtrip."""
        # Arrange
        shop1 = Shop.model_validate(sample_shop_dict)

        # Act
        dumped = shop1.model_dump()
        shop2 = Shop.model_validate(dumped)

        # Assert
        assert shop1.slug == shop2.slug
        assert shop1.name == shop2.name
        assert shop1.logo_url == shop2.logo_url


@pytest.mark.unit
class TestLeafletStatus:
    """Tests for LeafletStatus enum."""

    def test_enum_values(self):
        """Test all enum values are accessible."""
        # Assert
        assert LeafletStatus.ACTIVE == "active"
        assert LeafletStatus.ARCHIVED == "archived"
        assert LeafletStatus.UPCOMING == "upcoming"

    def test_enum_iteration(self):
        """Test enum can be iterated."""
        # Act
        values = list(LeafletStatus)

        # Assert
        assert len(values) == 3
        assert LeafletStatus.ACTIVE in values
        assert LeafletStatus.ARCHIVED in values
        assert LeafletStatus.UPCOMING in values

    def test_enum_from_string(self):
        """Test creating enum from string."""
        # Act & Assert
        assert LeafletStatus("active") == LeafletStatus.ACTIVE
        assert LeafletStatus("archived") == LeafletStatus.ARCHIVED
        assert LeafletStatus("upcoming") == LeafletStatus.UPCOMING

    def test_enum_invalid_string(self):
        """Test creating enum from invalid string raises error."""
        # Act & Assert
        with pytest.raises(ValueError):
            LeafletStatus("invalid")


@pytest.mark.unit
class TestLeaflet:
    """Comprehensive tests for Leaflet entity."""

    # ========== Valid Creation Tests ==========

    def test_create_leaflet_with_all_fields(self, sample_leaflet_dict):
        """Test creating leaflet with all fields populated."""
        # Arrange
        leaflet_data = sample_leaflet_dict.copy()

        # Act
        leaflet = Leaflet.model_validate(leaflet_data)

        # Assert
        assert leaflet.leaflet_id == 457727
        assert leaflet.shop_slug == "biedronka"
        assert leaflet.name == "Od środy"
        assert leaflet.status == LeafletStatus.ACTIVE
        assert leaflet.page_count == 12

    def test_create_leaflet_minimal_fields(self):
        """Test creating leaflet with only required fields."""
        # Arrange
        leaflet_data = {
            "leaflet_id": 123,
            "shop_slug": "test",
            "name": "Test Leaflet",
            "cover_image_url": "https://example.com/cover.jpg",
            "url": "https://example.com/leaflet",
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "status": "active",
        }

        # Act
        leaflet = Leaflet.model_validate(leaflet_data)

        # Assert
        assert leaflet.leaflet_id == 123
        assert leaflet.page_count is None

    def test_leaflet_scraped_at_default(self):
        """Test that scraped_at defaults to current UTC time."""
        # Arrange
        leaflet_data = {
            "leaflet_id": 123,
            "shop_slug": "test",
            "name": "Test",
            "cover_image_url": "https://example.com/cover.jpg",
            "url": "https://example.com/leaflet",
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "status": "active",
        }

        # Act
        before = datetime.now(timezone.utc)
        leaflet = Leaflet.model_validate(leaflet_data)
        after = datetime.now(timezone.utc)

        # Assert
        assert before <= leaflet.scraped_at <= after
        assert leaflet.scraped_at.tzinfo == timezone.utc

    # ========== Validation Tests ==========

    @pytest.mark.parametrize(
        "leaflet_id,should_fail",
        [
            (1, False),
            (100, False),
            (457727, False),
            (0, True),  # Must be > 0
            (-1, True),
            (-100, True),
        ],
    )
    def test_leaflet_id_validation(self, leaflet_id, should_fail, sample_leaflet_dict):
        """Test leaflet_id validation (gt=0)."""
        # Arrange
        leaflet_data = sample_leaflet_dict.copy()
        leaflet_data["leaflet_id"] = leaflet_id

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                Leaflet.model_validate(leaflet_data)
            assert "leaflet_id" in str(exc_info.value).lower()
        else:
            leaflet = Leaflet.model_validate(leaflet_data)
            assert leaflet.leaflet_id == leaflet_id

    @pytest.mark.parametrize(
        "status,expected_enum",
        [
            ("active", LeafletStatus.ACTIVE),
            ("archived", LeafletStatus.ARCHIVED),
            ("upcoming", LeafletStatus.UPCOMING),
            (LeafletStatus.ACTIVE, LeafletStatus.ACTIVE),
        ],
    )
    def test_leaflet_status_validation(self, status, expected_enum, sample_leaflet_dict):
        """Test leaflet status accepts string and enum."""
        # Arrange
        leaflet_data = sample_leaflet_dict.copy()
        leaflet_data["status"] = status

        # Act
        leaflet = Leaflet.model_validate(leaflet_data)

        # Assert
        assert leaflet.status == expected_enum

    def test_leaflet_status_invalid(self, sample_leaflet_dict):
        """Test leaflet status rejects invalid value."""
        # Arrange
        leaflet_data = sample_leaflet_dict.copy()
        leaflet_data["status"] = "invalid"

        # Act & Assert
        with pytest.raises(ValidationError):
            Leaflet.model_validate(leaflet_data)

    @pytest.mark.parametrize(
        "page_count,should_be_none",
        [
            (1, False),
            (12, False),
            (100, False),
            (None, True),
        ],
    )
    def test_leaflet_page_count_optional(self, page_count, should_be_none, sample_leaflet_dict):
        """Test leaflet page_count is optional with ge=1 constraint."""
        # Arrange
        leaflet_data = sample_leaflet_dict.copy()
        leaflet_data["page_count"] = page_count

        # Act & Assert
        if should_be_none:
            leaflet = Leaflet.model_validate(leaflet_data)
            assert leaflet.page_count is None
        else:
            leaflet = Leaflet.model_validate(leaflet_data)
            assert leaflet.page_count == page_count

    def test_leaflet_page_count_invalid(self, sample_leaflet_dict):
        """Test leaflet page_count rejects invalid values."""
        # Arrange
        leaflet_data = sample_leaflet_dict.copy()
        leaflet_data["page_count"] = 0  # Must be ge=1

        # Act & Assert
        with pytest.raises(ValidationError):
            Leaflet.model_validate(leaflet_data)

    # ========== is_valid_on Method Tests ==========

    def test_is_valid_on_within_range(self, sample_leaflet_dict):
        """Test is_valid_on returns True for date within validity range."""
        # Arrange
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        valid_date = datetime(2025, 11, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Act
        result = leaflet.is_valid_on(valid_date)

        # Assert
        assert result is True

    def test_is_valid_on_before_start(self, sample_leaflet_dict):
        """Test is_valid_on returns False for date before valid_from."""
        # Arrange
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        before_date = datetime(2025, 10, 28, 23, 59, 59, tzinfo=timezone.utc)

        # Act
        result = leaflet.is_valid_on(before_date)

        # Assert
        assert result is False

    def test_is_valid_on_after_end(self, sample_leaflet_dict):
        """Test is_valid_on returns False for date after valid_until."""
        # Arrange
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        after_date = datetime(2025, 11, 6, 0, 0, 0, tzinfo=timezone.utc)

        # Act
        result = leaflet.is_valid_on(after_date)

        # Assert
        assert result is False

    def test_is_valid_on_at_start_boundary(self, sample_leaflet_dict):
        """Test is_valid_on returns True at valid_from boundary."""
        # Arrange
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        start_date = datetime(2025, 10, 29, 0, 0, 0, tzinfo=timezone.utc)

        # Act
        result = leaflet.is_valid_on(start_date)

        # Assert
        assert result is True

    def test_is_valid_on_at_end_boundary(self, sample_leaflet_dict):
        """Test is_valid_on returns True at valid_until boundary."""
        # Arrange
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        end_date = datetime(2025, 11, 5, 23, 59, 59, tzinfo=timezone.utc)

        # Act
        result = leaflet.is_valid_on(end_date)

        # Assert
        assert result is True

    def test_is_valid_on_with_naive_datetime(self, sample_leaflet_dict):
        """Test is_valid_on treats naive datetime as UTC."""
        # Arrange
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        naive_date = datetime(2025, 11, 1, 12, 0, 0)  # No timezone

        # Act
        result = leaflet.is_valid_on(naive_date)

        # Assert
        assert result is True

    def test_is_valid_on_with_naive_leaflet_dates(self):
        """Test is_valid_on when leaflet has naive datetimes."""
        # Arrange
        leaflet_data = {
            "leaflet_id": 123,
            "shop_slug": "test",
            "name": "Test",
            "cover_image_url": "https://example.com/cover.jpg",
            "url": "https://example.com/leaflet",
            "valid_from": datetime(2025, 1, 1),  # Naive
            "valid_until": datetime(2025, 1, 31),  # Naive
            "status": "active",
        }
        leaflet = Leaflet(**leaflet_data)
        test_date = datetime(2025, 1, 15, tzinfo=timezone.utc)

        # Act
        result = leaflet.is_valid_on(test_date)

        # Assert
        assert result is True

    # ========== is_active_now Method Tests ==========

    def test_is_active_now_true(self, sample_leaflet_dict):
        """Test is_active_now returns True for currently active leaflet."""
        # Arrange
        now = datetime.now(timezone.utc)
        leaflet_data = sample_leaflet_dict.copy()
        leaflet_data["valid_from"] = (now - timedelta(days=1)).isoformat()
        leaflet_data["valid_until"] = (now + timedelta(days=1)).isoformat()
        leaflet = Leaflet.model_validate(leaflet_data)

        # Act
        result = leaflet.is_active_now()

        # Assert
        assert result is True

    def test_is_active_now_false_expired(self, sample_leaflet_dict):
        """Test is_active_now returns False for expired leaflet."""
        # Arrange
        now = datetime.now(timezone.utc)
        leaflet_data = sample_leaflet_dict.copy()
        leaflet_data["valid_from"] = (now - timedelta(days=10)).isoformat()
        leaflet_data["valid_until"] = (now - timedelta(days=1)).isoformat()
        leaflet = Leaflet.model_validate(leaflet_data)

        # Act
        result = leaflet.is_active_now()

        # Assert
        assert result is False

    def test_is_active_now_false_upcoming(self, sample_leaflet_dict):
        """Test is_active_now returns False for upcoming leaflet."""
        # Arrange
        now = datetime.now(timezone.utc)
        leaflet_data = sample_leaflet_dict.copy()
        leaflet_data["valid_from"] = (now + timedelta(days=1)).isoformat()
        leaflet_data["valid_until"] = (now + timedelta(days=10)).isoformat()
        leaflet = Leaflet.model_validate(leaflet_data)

        # Act
        result = leaflet.is_active_now()

        # Assert
        assert result is False

    # ========== Serialization Tests ==========

    def test_leaflet_model_dump(self, sample_leaflet_dict):
        """Test Leaflet serialization to dictionary."""
        # Arrange
        leaflet = Leaflet.model_validate(sample_leaflet_dict)

        # Act
        dumped = leaflet.model_dump()

        # Assert
        assert isinstance(dumped, dict)
        assert dumped["leaflet_id"] == 457727
        assert dumped["status"] == "active"

    def test_leaflet_model_validate_roundtrip(self, sample_leaflet_dict):
        """Test Leaflet serialization and deserialization roundtrip."""
        # Arrange
        leaflet1 = Leaflet.model_validate(sample_leaflet_dict)

        # Act
        dumped = leaflet1.model_dump()
        leaflet2 = Leaflet.model_validate(dumped)

        # Assert
        assert leaflet1.leaflet_id == leaflet2.leaflet_id
        assert leaflet1.name == leaflet2.name
        assert leaflet1.status == leaflet2.status


@pytest.mark.unit
class TestOffer:
    """Comprehensive tests for Offer entity."""

    # ========== Valid Creation Tests ==========

    def test_create_offer_with_price(self):
        """Test creating offer with price."""
        # Arrange
        offer_data = {
            "leaflet_id": 457727,
            "name": "Kurczak",
            "price": "12.99",
            "image_url": "https://blix.pl/offer/123.jpg",
            "page_number": 1,
            "position_x": 0.1,
            "position_y": 0.2,
            "width": 0.3,
            "height": 0.4,
            "valid_from": "2025-10-29T00:00:00Z",
            "valid_until": "2025-11-05T23:59:59Z",
            "scraped_at": "2025-10-30T12:00:00Z",
        }

        # Act
        offer = Offer.model_validate(offer_data)

        # Assert
        assert offer.name == "Kurczak"
        assert offer.price == Decimal("12.99")
        assert offer.page_number == 1

    def test_create_offer_without_price(self):
        """Test creating offer without price (optional field)."""
        # Arrange
        offer_data = {
            "leaflet_id": 457727,
            "name": "Product",
            "price": None,
            "image_url": "https://blix.pl/offer/123.jpg",
            "page_number": 1,
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "valid_from": "2025-10-29T00:00:00Z",
            "valid_until": "2025-11-05T23:59:59Z",
            "scraped_at": "2025-10-30T12:00:00Z",
        }

        # Act
        offer = Offer.model_validate(offer_data)

        # Assert
        assert offer.price is None

    def test_offer_scraped_at_default(self):
        """Test that scraped_at defaults to current UTC time."""
        # Arrange
        offer_data = {
            "leaflet_id": 123,
            "name": "Test",
            "image_url": "https://example.com/image.jpg",
            "page_number": 1,
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
        }

        # Act
        before = datetime.now(timezone.utc)
        offer = Offer.model_validate(offer_data)
        after = datetime.now(timezone.utc)

        # Assert
        assert before <= offer.scraped_at <= after
        assert offer.scraped_at.tzinfo == timezone.utc

    # ========== Validation Tests ==========

    @pytest.mark.parametrize(
        "price,expected_value",
        [
            ("12.99", Decimal("12.99")),
            ("0.01", Decimal("0.01")),
            ("999.99", Decimal("999.99")),
            (Decimal("12.99"), Decimal("12.99")),
            (None, None),
        ],
    )
    def test_offer_price_validation(self, price, expected_value):
        """Test offer price accepts various formats."""
        # Arrange
        offer_data = {
            "leaflet_id": 123,
            "name": "Test",
            "price": price,
            "image_url": "https://example.com/image.jpg",
            "page_number": 1,
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
        }

        # Act
        offer = Offer.model_validate(offer_data)

        # Assert
        assert offer.price == expected_value

    def test_offer_price_invalid_decimals(self):
        """Test offer price rejects values with more than 2 decimal places."""
        # Arrange
        offer_data = {
            "leaflet_id": 123,
            "name": "Test",
            "price": "12.999",  # 3 decimal places
            "image_url": "https://example.com/image.jpg",
            "page_number": 1,
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            Offer.model_validate(offer_data)

    @pytest.mark.parametrize(
        "page_number,should_fail",
        [
            (1, False),
            (10, False),
            (100, False),
            (0, True),  # Must be ge=1
            (-1, True),
        ],
    )
    def test_offer_page_number_validation(self, page_number, should_fail):
        """Test offer page_number validation (ge=1)."""
        # Arrange
        offer_data = {
            "leaflet_id": 123,
            "name": "Test",
            "price": None,
            "image_url": "https://example.com/image.jpg",
            "page_number": page_number,
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
        }

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError):
                Offer.model_validate(offer_data)
        else:
            offer = Offer.model_validate(offer_data)
            assert offer.page_number == page_number

    @pytest.mark.parametrize(
        "position_field,value,should_fail",
        [
            ("position_x", 0.0, False),
            ("position_x", 0.5, False),
            ("position_x", 1.0, False),
            ("position_x", -0.1, True),
            ("position_x", 1.1, True),
            ("position_y", 0.0, False),
            ("position_y", 1.0, False),
            ("position_y", -0.1, True),
            ("width", 0.0, False),
            ("width", 1.0, False),
            ("width", 1.1, True),
            ("height", 0.0, False),
            ("height", 1.0, False),
            ("height", -0.1, True),
        ],
    )
    def test_offer_position_validation(self, position_field, value, should_fail):
        """Test offer position fields validation (ge=0, le=1)."""
        # Arrange
        offer_data = {
            "leaflet_id": 123,
            "name": "Test",
            "price": None,
            "image_url": "https://example.com/image.jpg",
            "page_number": 1,
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
        }
        offer_data[position_field] = value

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError):
                Offer.model_validate(offer_data)
        else:
            offer = Offer.model_validate(offer_data)
            assert getattr(offer, position_field) == value

    # ========== Serialization Tests ==========

    def test_offer_model_dump(self):
        """Test Offer serialization to dictionary."""
        # Arrange
        offer_data = {
            "leaflet_id": 457727,
            "name": "Kurczak",
            "price": "12.99",
            "image_url": "https://blix.pl/offer/123.jpg",
            "page_number": 1,
            "position_x": 0.1,
            "position_y": 0.2,
            "width": 0.3,
            "height": 0.4,
            "valid_from": "2025-10-29T00:00:00Z",
            "valid_until": "2025-11-05T23:59:59Z",
        }

        # Act
        offer = Offer.model_validate(offer_data)
        dumped = offer.model_dump()

        # Assert
        assert isinstance(dumped, dict)
        assert dumped["name"] == "Kurczak"
        assert dumped["price"] == Decimal("12.99")

    def test_offer_model_validate_roundtrip(self):
        """Test Offer serialization and deserialization roundtrip."""
        # Arrange
        offer_data = {
            "leaflet_id": 457727,
            "name": "Kurczak",
            "price": "12.99",
            "image_url": "https://blix.pl/offer/123.jpg",
            "page_number": 1,
            "position_x": 0.1,
            "position_y": 0.2,
            "width": 0.3,
            "height": 0.4,
            "valid_from": "2025-10-29T00:00:00Z",
            "valid_until": "2025-11-05T23:59:59Z",
        }

        # Act
        offer1 = Offer.model_validate(offer_data)
        dumped = offer1.model_dump()
        offer2 = Offer.model_validate(dumped)

        # Assert
        assert offer1.name == offer2.name
        assert offer1.price == offer2.price
        assert offer1.position_x == offer2.position_x


@pytest.mark.unit
class TestSearchResult:
    """Comprehensive tests for SearchResult entity."""

    # ========== Valid Creation Tests ==========

    def test_create_search_result_minimal(self):
        """Test creating search result with minimal required fields."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product Name",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test query",
        }

        # Act
        result = SearchResult.model_validate(search_data)

        # Assert
        assert result.hash == "abc123"
        assert result.name == "Product Name"
        assert result.leaflet_id == 457727

    def test_create_search_result_with_all_fields(self):
        """Test creating search result with all fields populated."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product Name",
            "image_url": "https://example.com/image.jpg",
            "manufacturer_name": "Manufacturer",
            "manufacturer_uuid": "mfg-uuid",
            "brand_name": "Brand",
            "brand_uuid": "brand-uuid",
            "sub_brand_name": "Sub Brand",
            "sub_brand_uuid": "sub-brand-uuid",
            "hiper_category_id": 10,
            "offer_subcategory_id": 20,
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "price": "1299",  # 12.99 PLN in grosz
            "percent_discount": 20,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.1,
            "position_y": 0.2,
            "width": 0.3,
            "height": 0.4,
            "search_query": "test query",
            "shop_name": "Test Shop",
        }

        # Act
        result = SearchResult.model_validate(search_data)

        # Assert
        assert result.manufacturer_name == "Manufacturer"
        assert result.brand_name == "Brand"
        assert result.price == Decimal("1299")
        assert result.percent_discount == 20

    def test_search_result_scraped_at_default(self):
        """Test that scraped_at defaults to current UTC time."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }

        # Act
        before = datetime.now(timezone.utc)
        result = SearchResult.model_validate(search_data)
        after = datetime.now(timezone.utc)

        # Assert
        assert before <= result.scraped_at <= after
        assert result.scraped_at.tzinfo == timezone.utc

    # ========== Validation Tests ==========

    @pytest.mark.parametrize(
        "hash_value",
        [
            "abc123",
            "hash-with-dashes",
            "UPPERCASE_HASH",
            "   ",  # Whitespace is valid
            "",  # Empty string is valid (no min_length constraint)
        ],
    )
    def test_search_result_hash_validation(self, hash_value):
        """Test search result hash accepts various string values."""
        # Arrange
        search_data = {
            "hash": hash_value,
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }

        # Act
        result = SearchResult.model_validate(search_data)

        # Assert
        assert result.hash == hash_value

    @pytest.mark.parametrize(
        "name,should_fail",
        [
            ("Valid Name", False),
            ("Product-123", False),
            ("   ", False),  # Whitespace is valid (length > 0)
            ("", True),  # min_length=1
        ],
    )
    def test_search_result_name_validation(self, name, should_fail):
        """Test search result name validation (min_length=1)."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": name,
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError):
                SearchResult.model_validate(search_data)
        else:
            result = SearchResult.model_validate(search_data)
            assert result.name == name

    @pytest.mark.parametrize(
        "percent_discount,should_fail",
        [
            (0, False),
            (50, False),
            (100, False),
            (-1, True),  # Must be ge=0
            (101, True),  # Must be le=100
        ],
    )
    def test_search_result_percent_discount_validation(self, percent_discount, should_fail):
        """Test search result percent_discount validation (ge=0, le=100)."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "percent_discount": percent_discount,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError):
                SearchResult.model_validate(search_data)
        else:
            result = SearchResult.model_validate(search_data)
            assert result.percent_discount == percent_discount

    @pytest.mark.parametrize(
        "page_number,should_fail",
        [
            (0, False),
            (1, False),
            (10, False),
            (-1, True),  # Must be ge=0
        ],
    )
    def test_search_result_page_number_validation(self, page_number, should_fail):
        """Test search result page_number validation (ge=0)."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": page_number,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError):
                SearchResult.model_validate(search_data)
        else:
            result = SearchResult.model_validate(search_data)
            assert result.page_number == page_number

    @pytest.mark.parametrize(
        "position_field,value,should_fail",
        [
            ("position_x", 0.0, False),
            ("position_x", 0.5, False),
            ("position_x", 1.0, False),
            ("position_x", -0.1, True),
            ("position_x", 1.1, True),
            ("position_y", 0.0, False),
            ("position_y", 1.0, False),
            ("position_y", -0.1, True),
            ("width", 0.0, False),
            ("width", 1.0, False),
            ("width", 1.1, True),
            ("height", 0.0, False),
            ("height", 1.0, False),
            ("height", -0.1, True),
        ],
    )
    def test_search_result_position_validation(self, position_field, value, should_fail):
        """Test search result position fields validation (ge=0, le=1)."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }
        search_data[position_field] = value

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError):
                SearchResult.model_validate(search_data)
        else:
            result = SearchResult.model_validate(search_data)
            assert getattr(result, position_field) == value

    # ========== price_pln Property Tests ==========

    def test_price_pln_with_price(self):
        """Test price_pln property converts grosz to PLN."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "price": "1299",  # 12.99 PLN
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }

        # Act
        result = SearchResult.model_validate(search_data)
        price_pln = result.price_pln

        # Assert
        assert price_pln == Decimal("12.99")

    def test_price_pln_without_price(self):
        """Test price_pln property returns None when price is None."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "price": None,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }

        # Act
        result = SearchResult.model_validate(search_data)
        price_pln = result.price_pln

        # Assert
        assert price_pln is None

    @pytest.mark.parametrize(
        "price_grosz,expected_pln",
        [
            ("0", Decimal("0")),
            ("1", Decimal("0.01")),
            ("99", Decimal("0.99")),
            ("100", Decimal("1.00")),
            ("1299", Decimal("12.99")),
            ("9999", Decimal("99.99")),
        ],
    )
    def test_price_pln_conversion(self, price_grosz, expected_pln):
        """Test price_pln conversion for various values."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "price": price_grosz,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }

        # Act
        result = SearchResult.model_validate(search_data)

        # Assert
        assert result.price_pln == expected_pln

    # ========== to_offer Method Tests ==========

    def test_to_offer_conversion(self):
        """Test converting SearchResult to Offer entity."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "price": "1299",  # 12.99 PLN
            "percent_discount": 20,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.1,
            "position_y": 0.2,
            "width": 0.3,
            "height": 0.4,
            "search_query": "test",
        }
        search_result = SearchResult.model_validate(search_data)

        # Act
        offer = search_result.to_offer()

        # Assert
        assert isinstance(offer, Offer)
        assert offer.leaflet_id == 457727
        assert offer.name == "Product"
        assert offer.price == Decimal("12.99")
        assert offer.image_url == search_result.image_url
        assert offer.page_number == 1
        assert offer.position_x == 0.1
        assert offer.position_y == 0.2
        assert offer.width == 0.3
        assert offer.height == 0.4

    def test_to_offer_without_price(self):
        """Test converting SearchResult to Offer when price is None."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "price": None,
            "percent_discount": 0,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.0,
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "search_query": "test",
        }
        search_result = SearchResult.model_validate(search_data)

        # Act
        offer = search_result.to_offer()

        # Assert
        assert offer.price is None

    # ========== Serialization Tests ==========

    def test_search_result_model_dump(self):
        """Test SearchResult serialization to dictionary."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "price": "1299",
            "percent_discount": 20,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.1,
            "position_y": 0.2,
            "width": 0.3,
            "height": 0.4,
            "search_query": "test",
        }

        # Act
        result = SearchResult.model_validate(search_data)
        dumped = result.model_dump()

        # Assert
        assert isinstance(dumped, dict)
        assert dumped["hash"] == "abc123"
        assert dumped["name"] == "Product"
        assert dumped["price"] == Decimal("1299")

    def test_search_result_model_validate_roundtrip(self):
        """Test SearchResult serialization and deserialization roundtrip."""
        # Arrange
        search_data = {
            "hash": "abc123",
            "name": "Product",
            "image_url": "https://example.com/image.jpg",
            "product_leaflet_page_uuid": "uuid-123",
            "leaflet_id": 457727,
            "page_number": 1,
            "price": "1299",
            "percent_discount": 20,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-01-31T23:59:59Z",
            "position_x": 0.1,
            "position_y": 0.2,
            "width": 0.3,
            "height": 0.4,
            "search_query": "test",
        }

        # Act
        result1 = SearchResult.model_validate(search_data)
        dumped = result1.model_dump()
        result2 = SearchResult.model_validate(dumped)

        # Assert
        assert result1.hash == result2.hash
        assert result1.name == result2.name
        assert result1.price == result2.price


@pytest.mark.unit
class TestKeyword:
    """Comprehensive tests for Keyword entity."""

    # ========== Valid Creation Tests ==========

    def test_create_keyword(self):
        """Test creating keyword with all fields."""
        # Arrange
        keyword_data = {
            "leaflet_id": 457727,
            "text": "kurczak",
            "url": "/produkty/mieso/kurczak",
            "category_path": "mieso/kurczak",
            "scraped_at": "2025-10-30T12:00:00Z",
        }

        # Act
        keyword = Keyword.model_validate(keyword_data)

        # Assert
        assert keyword.text == "kurczak"
        assert keyword.category_path == "mieso/kurczak"

    def test_keyword_scraped_at_default(self):
        """Test that scraped_at defaults to current UTC time."""
        # Arrange
        keyword_data = {
            "leaflet_id": 123,
            "text": "test",
            "url": "/test",
            "category_path": "test",
        }

        # Act
        before = datetime.now(timezone.utc)
        keyword = Keyword.model_validate(keyword_data)
        after = datetime.now(timezone.utc)

        # Assert
        assert before <= keyword.scraped_at <= after
        assert keyword.scraped_at.tzinfo == timezone.utc

    # ========== Validation Tests ==========

    @pytest.mark.parametrize(
        "text,should_fail",
        [
            ("valid", False),
            ("with-dash", False),
            ("with_underscore", False),
            ("UPPERCASE", False),
            ("   ", False),  # Whitespace is valid (length > 0)
            ("", True),  # min_length=1
        ],
    )
    def test_keyword_text_validation(self, text, should_fail):
        """Test keyword text validation (min_length=1)."""
        # Arrange
        keyword_data = {
            "leaflet_id": 123,
            "text": text,
            "url": "/test",
            "category_path": "test",
        }

        # Act & Assert
        if should_fail:
            with pytest.raises(ValidationError):
                Keyword.model_validate(keyword_data)
        else:
            keyword = Keyword.model_validate(keyword_data)
            assert keyword.text == text

    # ========== Hash and Equality Tests ==========

    def test_keyword_hash_based_on_text(self):
        """Test keyword hashing is based on text field only."""
        # Arrange
        kw1 = Keyword(
            leaflet_id=1,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc),
        )

        kw2 = Keyword(
            leaflet_id=2,
            text="kurczak",
            url="/produkty/mieso/kurczak",
            category_path="mieso/kurczak",
            scraped_at=datetime.now(timezone.utc),
        )

        # Act & Assert
        assert hash(kw1) == hash(kw2)

    def test_keyword_hash_different_text(self):
        """Test keywords with different text have different hashes."""
        # Arrange
        kw1 = Keyword(
            leaflet_id=1,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc),
        )

        kw2 = Keyword(
            leaflet_id=1,
            text="mieso",
            url="/produkty/mieso",
            category_path="mieso",
            scraped_at=datetime.now(timezone.utc),
        )

        # Act & Assert
        assert hash(kw1) != hash(kw2)

    def test_keyword_equality_same_text(self):
        """Test keywords with same text are equal."""
        # Arrange
        kw1 = Keyword(
            leaflet_id=1,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc),
        )

        kw2 = Keyword(
            leaflet_id=2,
            text="kurczak",
            url="/produkty/mieso/kurczak",
            category_path="mieso/kurczak",
            scraped_at=datetime.now(timezone.utc),
        )

        # Act & Assert
        assert kw1 == kw2

    def test_keyword_equality_different_text(self):
        """Test keywords with different text are not equal."""
        # Arrange
        kw1 = Keyword(
            leaflet_id=1,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc),
        )

        kw2 = Keyword(
            leaflet_id=1,
            text="mieso",
            url="/produkty/mieso",
            category_path="mieso",
            scraped_at=datetime.now(timezone.utc),
        )

        # Act & Assert
        assert kw1 != kw2

    def test_keyword_equality_with_non_keyword(self):
        """Test keyword equality with non-Keyword object returns False."""
        # Arrange
        keyword = Keyword(
            leaflet_id=1,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc),
        )

        # Act & Assert
        assert keyword != "kurczak"
        assert keyword != 123
        assert keyword is not None
        assert keyword != {"text": "kurczak"}

    def test_keyword_can_be_used_in_set(self):
        """Test keywords can be used in sets (based on hash/eq)."""
        # Arrange
        kw1 = Keyword(
            leaflet_id=1,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc),
        )

        kw2 = Keyword(
            leaflet_id=2,
            text="kurczak",
            url="/other/kurczak",
            category_path="other",
            scraped_at=datetime.now(timezone.utc),
        )

        kw3 = Keyword(
            leaflet_id=1,
            text="mieso",
            url="/produkty/mieso",
            category_path="mieso",
            scraped_at=datetime.now(timezone.utc),
        )

        # Act
        keyword_set = {kw1, kw2, kw3}

        # Assert - kw1 and kw2 should be deduplicated since they have same text
        assert len(keyword_set) == 2
        assert any(kw.text == "kurczak" for kw in keyword_set)
        assert any(kw.text == "mieso" for kw in keyword_set)

    # ========== Serialization Tests ==========

    def test_keyword_model_dump(self):
        """Test Keyword serialization to dictionary."""
        # Arrange
        keyword_data = {
            "leaflet_id": 457727,
            "text": "kurczak",
            "url": "/produkty/mieso/kurczak",
            "category_path": "mieso/kurczak",
        }

        # Act
        keyword = Keyword.model_validate(keyword_data)
        dumped = keyword.model_dump()

        # Assert
        assert isinstance(dumped, dict)
        assert dumped["text"] == "kurczak"
        assert dumped["category_path"] == "mieso/kurczak"

    def test_keyword_model_validate_roundtrip(self):
        """Test Keyword serialization and deserialization roundtrip."""
        # Arrange
        keyword_data = {
            "leaflet_id": 457727,
            "text": "kurczak",
            "url": "/produkty/mieso/kurczak",
            "category_path": "mieso/kurczak",
        }

        # Act
        keyword1 = Keyword.model_validate(keyword_data)
        dumped = keyword1.model_dump()
        keyword2 = Keyword.model_validate(dumped)

        # Assert
        assert keyword1.text == keyword2.text
        assert keyword1.category_path == keyword2.category_path
