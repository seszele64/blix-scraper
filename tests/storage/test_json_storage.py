"""Tests for JSON storage."""

import pytest
from pathlib import Path
import json
import tempfile
import shutil

from src.storage.json_storage import JSONStorage
from src.domain.entities import Shop


@pytest.fixture
def temp_storage_dir():
    """Create temporary directory for storage tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def shop_storage(temp_storage_dir):
    """Create shop storage instance."""
    return JSONStorage(temp_storage_dir, Shop)


class TestJSONStorage:
    """Tests for JSONStorage class."""
    
    def test_save_entity(self, shop_storage, sample_shop_dict, temp_storage_dir):
        """Test saving entity to JSON file."""
        shop = Shop.model_validate(sample_shop_dict)
        
        shop_storage.save(shop, "biedronka.json")
        
        # Check file exists
        file_path = temp_storage_dir / "biedronka.json"
        assert file_path.exists()
        
        # Check content
        with open(file_path) as f:
            data = json.load(f)
        
        assert data["slug"] == "biedronka"
        assert data["name"] == "Biedronka"
    
    def test_load_entity(self, shop_storage, sample_shop_dict, temp_storage_dir):
        """Test loading entity from JSON file."""
        # Save first
        shop = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop, "biedronka.json")
        
        # Load
        loaded_shop = shop_storage.load("biedronka.json")
        
        assert loaded_shop is not None
        assert loaded_shop.slug == "biedronka"
        assert loaded_shop.name == "Biedronka"
        assert isinstance(loaded_shop, Shop)
    
    def test_load_nonexistent_file(self, shop_storage):
        """Test loading non-existent file returns None."""
        result = shop_storage.load("nonexistent.json")
        assert result is None
    
    def test_load_all(self, shop_storage, sample_shop_dict):
        """Test loading all entities from directory."""
        # Save multiple shops
        shop1 = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop1, "biedronka.json")
        
        sample_shop_dict["slug"] = "lidl"
        sample_shop_dict["name"] = "Lidl"
        shop2 = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop2, "lidl.json")
        
        # Load all
        shops = shop_storage.load_all()
        
        assert len(shops) == 2
        assert any(s.slug == "biedronka" for s in shops)
        assert any(s.slug == "lidl" for s in shops)
    
    def test_save_many(self, shop_storage, sample_shop_dict, temp_storage_dir):
        """Test saving multiple entities to single file."""
        shop1 = Shop.model_validate(sample_shop_dict)
        
        sample_shop_dict["slug"] = "lidl"
        sample_shop_dict["name"] = "Lidl"
        shop2 = Shop.model_validate(sample_shop_dict)
        
        shops = [shop1, shop2]
        shop_storage.save_many(shops, "all_shops.json")
        
        # Check file
        file_path = temp_storage_dir / "all_shops.json"
        assert file_path.exists()
        
        with open(file_path) as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]["slug"] == "biedronka"
        assert data[1]["slug"] == "lidl"
    
    def test_exists(self, shop_storage, sample_shop_dict):
        """Test checking file existence."""
        assert not shop_storage.exists("biedronka.json")
        
        shop = Shop.model_validate(sample_shop_dict)
        shop_storage.save(shop, "biedronka.json")
        
        assert shop_storage.exists("biedronka.json")