"""JSON file storage implementation."""

import json
from typing import List, Optional, Type, TypeVar
from pathlib import Path
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar('T', bound=BaseModel)


class JSONStorage:
    """JSON file storage for Pydantic models."""
    
    def __init__(self, data_dir: Path, model_class: Type[T]):
        """
        Initialize storage.
        
        Args:
            data_dir: Directory for JSON files
            model_class: Pydantic model class for validation
        """
        self.data_dir = Path(data_dir)
        self.model_class = model_class
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug("storage_initialized", data_dir=str(self.data_dir))
    
    def save(self, entity: T, filename: str) -> None:
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
                    ensure_ascii=False,
                    default=str
                )
            logger.info("entity_saved", filepath=str(filepath))
        except Exception as e:
            logger.error("save_failed", filepath=str(filepath), error=str(e))
            raise
    
    def load(self, filename: str) -> Optional[T]:
        """
        Load entity from JSON file.
        
        Args:
            filename: Source filename
            
        Returns:
            Pydantic model instance or None if not found
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.debug("file_not_found", filepath=str(filepath))
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            entity = self.model_class.model_validate(data)
            logger.debug("entity_loaded", filepath=str(filepath))
            return entity
        except Exception as e:
            logger.error("load_failed", filepath=str(filepath), error=str(e))
            return None
    
    def load_all(self) -> List[T]:
        """
        Load all JSON files in directory.
        
        Returns:
            List of Pydantic model instances
        """
        entities: List[T] = []
        
        for filepath in sorted(self.data_dir.glob("*.json")):
            entity = self.load(filepath.name)
            if entity:
                entities.append(entity)
        
        logger.debug("entities_loaded", count=len(entities))
        return entities
    
    def save_many(self, entities: List[T], filename: str) -> None:
        """
        Save multiple entities to single JSON file.
        
        Args:
            entities: List of Pydantic model instances
            filename: Target filename
        """
        filepath = self.data_dir / filename
        
        try:
            data = [e.model_dump(mode='json') for e in entities]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info("entities_saved", count=len(entities), filepath=str(filepath))
        except Exception as e:
            logger.error("save_many_failed", filepath=str(filepath), error=str(e))
            raise
    
    def exists(self, filename: str) -> bool:
        """Check if file exists."""
        return (self.data_dir / filename).exists()