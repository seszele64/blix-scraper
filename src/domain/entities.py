"""Domain entities for Blix scraper."""

from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from decimal import Decimal


class Shop(BaseModel):
    """Retail brand entity."""
    
    slug: str = Field(..., min_length=1, description="URL slug")
    brand_id: Optional[int] = Field(None, description="Blix brand ID")
    name: str = Field(..., min_length=1)
    logo_url: HttpUrl
    category: Optional[str] = None
    leaflet_count: int = Field(ge=0)
    is_popular: bool = False
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_schema_extra = {
            "example": {
                "slug": "biedronka",
                "brand_id": 23,
                "name": "Biedronka",
                "logo_url": "https://img.blix.pl/image/brand/thumbnail_23.jpg",
                "category": "Sklepy spożywcze",
                "leaflet_count": 13,
                "is_popular": True,
            }
        }


class LeafletStatus(str, Enum):
    """Leaflet availability status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    UPCOMING = "upcoming"


class Leaflet(BaseModel):
    """Promotional leaflet entity."""
    
    leaflet_id: int = Field(..., gt=0)
    shop_slug: str
    name: str
    cover_image_url: HttpUrl
    url: HttpUrl
    
    valid_from: datetime
    valid_until: datetime
    status: LeafletStatus
    
    page_count: Optional[int] = Field(None, ge=1)
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_valid_on(self, target_date: datetime) -> bool:
        """
        Check if leaflet is valid on given date.
        
        Args:
            target_date: Date to check (naive datetime will be treated as UTC)
            
        Returns:
            True if leaflet is valid on the given date
        """
        # Ensure target_date is timezone-aware (treat naive as UTC)
        if target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=timezone.utc)
        
        # Ensure valid_from and valid_until are timezone-aware
        valid_from = self.valid_from
        if valid_from.tzinfo is None:
            valid_from = valid_from.replace(tzinfo=timezone.utc)
        
        valid_until = self.valid_until
        if valid_until.tzinfo is None:
            valid_until = valid_until.replace(tzinfo=timezone.utc)
        
        return valid_from <= target_date <= valid_until
    
    def is_active_now(self) -> bool:
        """Check if leaflet is currently active."""
        return self.is_valid_on(datetime.now(timezone.utc))


class Offer(BaseModel):
    """Product offer within leaflet."""
    
    leaflet_id: int
    name: str
    price: Optional[Decimal] = Field(None, decimal_places=2)
    image_url: HttpUrl
    
    # Position metadata
    page_number: int = Field(ge=1)
    position_x: float = Field(ge=0, le=1)
    position_y: float = Field(ge=0, le=1)
    width: float = Field(ge=0, le=1)
    height: float = Field(ge=0, le=1)
    
    valid_from: datetime
    valid_until: datetime
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchResult(BaseModel):
    """Search result for a product from search engine."""
    
    hash: str = Field(..., description="Unique hash identifier")
    name: str = Field(..., min_length=1)
    image_url: HttpUrl
    
    # Brand/Manufacturer info
    manufacturer_name: Optional[str] = None
    manufacturer_uuid: Optional[str] = None
    brand_name: Optional[str] = None
    brand_uuid: Optional[str] = None
    sub_brand_name: Optional[str] = None
    sub_brand_uuid: Optional[str] = None
    
    # Category info
    hiper_category_id: Optional[int] = None
    offer_subcategory_id: Optional[int] = None
    
    # Leaflet/Page info
    product_leaflet_page_uuid: str
    leaflet_id: int
    page_number: int = Field(ge=0)
    
    # Price info
    price: Optional[Decimal] = Field(None, description="Price in grosz (1/100 PLN)")
    percent_discount: int = Field(ge=0, le=100)
    
    # Validity period
    valid_from: datetime
    valid_until: datetime
    
    # Position in leaflet
    position_x: float = Field(ge=0, le=1, description="Top-left X coordinate")
    position_y: float = Field(ge=0, le=1, description="Top-left Y coordinate")
    width: float = Field(ge=0, le=1, description="Width (bottom-right X - top-left X)")
    height: float = Field(ge=0, le=1, description="Height (bottom-right Y - top-left Y)")
    
    # Search metadata
    search_query: str = Field(..., description="Query that found this result")
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def price_pln(self) -> Optional[Decimal]:
        """Convert price from grosz to PLN."""
        if self.price is None:
            return None
        return self.price / 100
    
    def to_offer(self) -> Offer:
        """Convert SearchResult to Offer entity."""
        return Offer(
            leaflet_id=self.leaflet_id,
            name=self.name,
            price=self.price_pln,
            image_url=self.image_url,
            page_number=self.page_number,
            position_x=self.position_x,
            position_y=self.position_y,
            width=self.width,
            height=self.height,
            valid_from=self.valid_from,
            valid_until=self.valid_until,
            scraped_at=self.scraped_at
        )


class Keyword(BaseModel):
    """Product keyword/category tag."""
    
    leaflet_id: int
    text: str = Field(..., min_length=1)
    url: str
    category_path: str  # Parsed from URL
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __hash__(self) -> int:
        return hash(self.text)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Keyword):
            return False
        return self.text == other.text