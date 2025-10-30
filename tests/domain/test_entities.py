"""Tests for domain entities."""

import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pydantic import ValidationError

from src.domain.entities import Shop, Leaflet, LeafletStatus, Offer, Keyword


class TestShop:
    """Tests for Shop entity."""
    
    def test_create_shop_valid(self, sample_shop_dict):
        """Test creating shop with valid data."""
        shop = Shop.model_validate(sample_shop_dict)
        
        assert shop.slug == "biedronka"
        assert shop.name == "Biedronka"
        assert shop.is_popular is True
        assert shop.leaflet_count == 13
    
    def test_shop_requires_name(self, sample_shop_dict):
        """Test shop requires name."""
        sample_shop_dict["name"] = ""
        
        with pytest.raises(ValidationError) as exc_info:
            Shop.model_validate(sample_shop_dict)
        
        assert "name" in str(exc_info.value)
    
    def test_shop_validates_url(self, sample_shop_dict):
        """Test shop validates logo URL."""
        sample_shop_dict["logo_url"] = "not-a-url"
        
        with pytest.raises(ValidationError):
            Shop.model_validate(sample_shop_dict)
    
    def test_shop_negative_leaflet_count(self, sample_shop_dict):
        """Test shop rejects negative leaflet count."""
        sample_shop_dict["leaflet_count"] = -5
        
        with pytest.raises(ValidationError):
            Shop.model_validate(sample_shop_dict)


class TestLeaflet:
    """Tests for Leaflet entity."""
    
    def test_create_leaflet_valid(self, sample_leaflet_dict):
        """Test creating leaflet with valid data."""
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        
        assert leaflet.leaflet_id == 457727
        assert leaflet.shop_slug == "biedronka"
        assert leaflet.status == LeafletStatus.ACTIVE
    
    def test_is_valid_on_date(self, sample_leaflet_dict):
        """Test leaflet validity checking."""
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        
        # Valid date (timezone-aware)
        valid_date = datetime(2025, 11, 1, tzinfo=timezone.utc)
        assert leaflet.is_valid_on(valid_date) is True
        
        # Before start
        before_date = datetime(2025, 10, 28, tzinfo=timezone.utc)
        assert leaflet.is_valid_on(before_date) is False
        
        # After end
        after_date = datetime(2025, 11, 10, tzinfo=timezone.utc)
        assert leaflet.is_valid_on(after_date) is False
    
    def test_is_valid_on_date_naive(self, sample_leaflet_dict):
        """Test leaflet validity with naive datetime (treated as UTC)."""
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        
        # Naive datetime should be treated as UTC
        valid_date = datetime(2025, 11, 1)  # No timezone
        assert leaflet.is_valid_on(valid_date) is True
    
    def test_is_active_now(self, sample_leaflet_dict):
        """Test current activity check."""
        # Set dates around current time (timezone-aware)
        now = datetime.now(timezone.utc)
        sample_leaflet_dict["valid_from"] = (now - timedelta(days=1)).isoformat()
        sample_leaflet_dict["valid_until"] = (now + timedelta(days=1)).isoformat()
        
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        assert leaflet.is_active_now() is True
    
    def test_is_not_active_expired(self, sample_leaflet_dict):
        """Test expired leaflet is not active."""
        # Set dates in the past
        now = datetime.now(timezone.utc)
        sample_leaflet_dict["valid_from"] = (now - timedelta(days=10)).isoformat()
        sample_leaflet_dict["valid_until"] = (now - timedelta(days=1)).isoformat()
        
        leaflet = Leaflet.model_validate(sample_leaflet_dict)
        assert leaflet.is_active_now() is False


class TestOffer:
    """Tests for Offer entity."""
    
    def test_create_offer_with_price(self):
        """Test creating offer with price."""
        offer_dict = {
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
            "scraped_at": "2025-10-30T12:00:00Z"
        }
        
        offer = Offer.model_validate(offer_dict)
        
        assert offer.name == "Kurczak"
        assert offer.price == Decimal("12.99")
        assert offer.page_number == 1
    
    def test_create_offer_without_price(self):
        """Test creating offer without price (optional field)."""
        offer_dict = {
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
            "scraped_at": "2025-10-30T12:00:00Z"
        }
        
        offer = Offer.model_validate(offer_dict)
        assert offer.price is None
    
    def test_offer_validates_position(self):
        """Test offer validates position values (0-1 range)."""
        offer_dict = {
            "leaflet_id": 457727,
            "name": "Product",
            "price": None,
            "image_url": "https://blix.pl/offer/123.jpg",
            "page_number": 1,
            "position_x": 1.5,  # Invalid: > 1
            "position_y": 0.0,
            "width": 1.0,
            "height": 1.0,
            "valid_from": "2025-10-29T00:00:00Z",
            "valid_until": "2025-11-05T23:59:59Z",
            "scraped_at": "2025-10-30T12:00:00Z"
        }
        
        with pytest.raises(ValidationError):
            Offer.model_validate(offer_dict)


class TestKeyword:
    """Tests for Keyword entity."""
    
    def test_create_keyword(self):
        """Test creating keyword."""
        keyword_dict = {
            "leaflet_id": 457727,
            "text": "kurczak",
            "url": "/produkty/mieso/kurczak",
            "category_path": "mieso/kurczak",
            "scraped_at": "2025-10-30T12:00:00Z"
        }
        
        keyword = Keyword.model_validate(keyword_dict)
        
        assert keyword.text == "kurczak"
        assert keyword.category_path == "mieso/kurczak"
    
    def test_keyword_hash(self):
        """Test keyword hashing by text."""
        kw1 = Keyword(
            leaflet_id=1,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc)
        )
        
        kw2 = Keyword(
            leaflet_id=2,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc)
        )
        
        # Same text = same hash
        assert hash(kw1) == hash(kw2)
        assert kw1 == kw2
    
    def test_keyword_equality(self):
        """Test keyword equality by text."""
        kw1 = Keyword(
            leaflet_id=1,
            text="kurczak",
            url="/produkty/kurczak",
            category_path="kurczak",
            scraped_at=datetime.now(timezone.utc)
        )
        
        kw2 = Keyword(
            leaflet_id=1,
            text="mieso",
            url="/produkty/mieso",
            category_path="mieso",
            scraped_at=datetime.now(timezone.utc)
        )
        
        assert kw1 != kw2