# Domain Model Design (Revised)

## 1. Core Entities (Simplified)

### 1.1 Shop

```python
# filepath: /home/tr1x/programming/blix-scraper/src/domain/entities.py

from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class Shop(BaseModel):
    """
    Retail brand entity.
    
    Validated with Pydantic for type safety.
    """
    slug: str = Field(..., min_length=1, description="URL slug")
    brand_id: Optional[int] = Field(None, description="Blix brand ID")
    name: str = Field(..., min_length=1)
    logo_url: HttpUrl
    category: Optional[str] = None
    leaflet_count: int = Field(ge=0)
    is_popular: bool = False
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
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
                "scraped_at": "2025-10-30T12:00:00Z"
            }
        }
```

### 1.2 Leaflet

```python
from enum import Enum

class LeafletStatus(str, Enum):
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
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_valid_on(self, target_date: datetime) -> bool:
        """Check if leaflet is valid on given date."""
        return self.valid_from <= target_date <= self.valid_until
    
    def is_active_now(self) -> bool:
        """Check if leaflet is currently active."""
        return self.is_valid_on(datetime.utcnow())
```

### 1.3 Offer

```python
from decimal import Decimal

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
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
```

### 1.4 Keyword

```python
class Keyword(BaseModel):
    """Product keyword/category tag."""
    
    leaflet_id: int
    text: str = Field(..., min_length=1)
    url: str
    category_path: str  # Parsed from URL
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __hash__(self):
        return hash(self.text)
```

---

## 2. Persistence (JSON Export)

The project has no persistent storage layer or database. Scraped data is held in
memory by `src.services.scraper_service.ScraperService` and exported to JSON files
on demand via `src.utils.data_export`.

### 2.1 Exporting Data

```python
# filepath: /home/tr1x/programming/blix-scraper/src/utils/data_export.py

from pathlib import Path
from src.utils.data_export import save_to_json, generate_export_metadata

# Generate export metadata (timestamp, counts, etc.)
metadata = generate_export_metadata(...)

# Export a collection of entities to a JSON file
save_to_json(
    data=[shop.model_dump(mode="json") for shop in shops],
    output_path=Path("data/shops/shops.json"),
    metadata=metadata,
)
```

Scrapers and the CLI collect entities in memory and write them out as JSON files
using `save_to_json`. There is no repository or storage abstraction layer.