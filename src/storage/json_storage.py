"""JSON file storage implementation."""

import json
from typing import List, Optional, TypeVar
from pathlib import Path
from pydantic import BaseModel
import structlog

from .field_filter import FieldFilter

logger = structlog.get_logger(__name__)

T = TypeVar('T', bound=BaseModel)


class JSONStorage:
    """
    Storage handler for saving entities as JSON files.
    
    Handles serialization and deserialization of domain entities.
    """
    
    def __init__(self, base_dir: Path, entity_type: type):
        """
        Initialize JSON storage.
        
        Args:
            base_dir: Base directory for storage
            entity_type: Type of entity being stored
        """
        self.base_dir = Path(base_dir)
        self.entity_type = entity_type
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("storage_initialized", base_dir=str(self.base_dir))
    
    def save(
        self,
        entity: BaseModel,
        filename: str,
        field_filter: Optional[FieldFilter] = None
    ) -> Path:
        """
        Save a single entity to JSON file.
        
        Args:
            entity: Entity to save
            filename: Name of the file
            field_filter: Optional field filter to apply
            
        Returns:
            Path to saved file
        """
        filepath = self.base_dir / filename
        
        # Apply field filter if provided
        if field_filter:
            data = field_filter.filter_entity(entity)
        else:
            data = entity.model_dump()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info("entity_saved", filepath=str(filepath))
        return filepath
    
    def save_many(
        self,
        entities: List[BaseModel],
        filename: str,
        field_filter: Optional[FieldFilter] = None
    ) -> Path:
        """
        Save multiple entities to a JSON file.
        
        Args:
            entities: List of entities to save
            filename: Name of the file
            field_filter: Optional field filter to apply
            
        Returns:
            Path to saved file
        """
        filepath = self.base_dir / filename
        
        # Apply field filter if provided
        if field_filter:
            data = field_filter.filter_many(entities)
        else:
            data = [entity.model_dump() for entity in entities]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(
            "entities_saved",
            filepath=str(filepath),
            count=len(entities)
        )
        return filepath
    
    def load(self, filename: str) -> Optional[BaseModel]:
        """
        Load entity from JSON file.
        
        Args:
            filename: Source filename
            
        Returns:
            Pydantic model instance or None if not found
        """
        filepath = self.base_dir / filename
        
        if not filepath.exists():
            logger.debug("file_not_found", filepath=str(filepath))
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            entity = self.entity_type.model_validate(data)
            logger.debug("entity_loaded", filepath=str(filepath))
            return entity
        except Exception as e:
            logger.error("load_failed", filepath=str(filepath), error=str(e))
            return None
    
    def load_all(self) -> List[BaseModel]:
        """
        Load all JSON files in directory.
        
        Returns:
            List of Pydantic model instances
        """
        entities: List[BaseModel] = []
        
        for filepath in sorted(self.base_dir.glob("*.json")):
            entity = self.load(filepath.name)
            if entity:
                entities.append(entity)
        
        logger.debug("entities_loaded", count=len(entities))
        return entities
    
    def exists(self, filename: str) -> bool:
        """Check if file exists."""
        return (self.base_dir / filename).exists()