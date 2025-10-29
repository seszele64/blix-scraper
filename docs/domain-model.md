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

## 2. Storage Layer (File-Based)

### 2.1 Base Storage Interface

```python
# filepath: /home/tr1x/programming/blix-scraper/src/storage/base.py

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from pathlib import Path

T = TypeVar('T')

class BaseStorage(ABC, Generic[T]):
    """
    Abstract storage interface for file-based persistence.
    
    No database - just JSON files.
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def save(self, entity: T, filename: str) -> None:
        """Save entity to JSON file."""
        pass
    
    @abstractmethod
    def load(self, filename: str) -> Optional[T]:
        """Load entity from JSON file."""
        pass
    
    @abstractmethod
    def load_all(self) -> List[T]:
        """Load all entities from directory."""
        pass
```

### 2.2 JSON Storage Implementation

```python
# filepath: /home/tr1x/programming/blix-scraper/src/storage/json_storage.py

import json
from typing import List, Optional, Type
from pathlib import Path
from pydantic import BaseModel
from .base import BaseStorage
import structlog

logger = structlog.get_logger(__name__)

class JSONStorage(BaseStorage[BaseModel]):
    """
    JSON file storage implementation.
    
    Uses Pydantic models for validation.
    """
    
    def __init__(self, data_dir: Path, model_class: Type[BaseModel]):
        super().__init__(data_dir)
        self.model_class = model_class
    
    def save(self, entity: BaseModel, filename: str) -> None:
        """
        Save entity to JSON file.
        
        Args:
            entity: Pydantic model instance
            filename: Target filename (e.g., "biedronka.json")
        """
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    entity.model_dump(mode='json'),
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            logger.info("entity_saved", filepath=str(filepath))
        except Exception as e:
            logger.error("save_failed", filepath=str(filepath), error=str(e))
            raise
    
    def load(self, filename: str) -> Optional[BaseModel]:
        """Load entity from JSON file."""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self.model_class.model_validate(data)
        except Exception as e:
            logger.error("load_failed", filepath=str(filepath), error=str(e))
            return None
    
    def load_all(self) -> List[BaseModel]:
        """Load all JSON files in directory."""
        entities = []
        
        for filepath in self.data_dir.glob("*.json"):
            entity = self.load(filepath.name)
            if entity:
                entities.append(entity)
        
        return entities
    
    def save_many(self, entities: List[BaseModel], filename: str) -> None:
        """
        Save multiple entities to single JSON file.
        
        Useful for collections (e.g., all shops).
        """
        filepath = self.data_dir / filename
        
        try:
            data = [e.model_dump(mode='json') for e in entities]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("entities_saved", count=len(entities), filepath=str(filepath))
        except Exception as e:
            logger.error("save_many_failed", filepath=str(filepath), error=str(e))
            raise
```

---

## 3. No Repositories - Direct Storage Access

Since we're using files, we don't need repository abstraction. Scrapers save directly:

```python
# Example usage in scraper
from pathlib import Path
from src.storage.json_storage import JSONStorage
from src.domain.entities import Shop

# Initialize storage
shops_storage = JSONStorage(
    data_dir=Path("data/shops"),
    model_class=Shop
)

# Save shop
shop = Shop(slug="biedronka", name="Biedronka", ...)
shops_storage.save(shop, "biedronka.json")

# Load shop
shop = shops_storage.load("biedronka.json")

# Load all shops
all_shops = shops_storage.load_all()
```