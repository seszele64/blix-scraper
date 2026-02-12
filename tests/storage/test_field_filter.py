"""Unit tests for field_filter module."""

from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from src.storage.field_filter import FieldFilter


@pytest.mark.unit
class TestFieldFilterInitialization:
    """Test FieldFilter class initialization."""

    def test_init_default_uses_base_schema(self):
        """Test that default initialization uses base schema."""
        # Arrange
        filter_obj = FieldFilter()

        # Act
        result = filter_obj.fields

        # Assert
        assert result == FieldFilter.BASE_SCHEMA

    def test_init_with_custom_fields_no_base(self):
        """Test initialization with custom fields without base schema."""
        # Arrange
        custom_fields = {"name", "price", "custom_field"}

        # Act
        filter_obj = FieldFilter(include_fields=custom_fields, use_base=False)

        # Assert
        assert filter_obj.fields == custom_fields

    def test_init_with_custom_fields_with_base(self):
        """Test initialization with custom fields combined with base schema."""
        # Arrange
        custom_fields = {"custom_field1", "custom_field2"}

        # Act
        filter_obj = FieldFilter(include_fields=custom_fields, use_base=True)

        # Assert
        expected = FieldFilter.BASE_SCHEMA | custom_fields
        assert filter_obj.fields == expected

    def test_init_with_none_include_fields(self):
        """Test that None include_fields uses base schema."""
        # Arrange
        filter_obj = FieldFilter(include_fields=None, use_base=False)

        # Act
        result = filter_obj.fields

        # Assert
        assert result == FieldFilter.BASE_SCHEMA

    def test_init_empty_fields_set(self):
        """Test initialization with empty fields set."""
        # Arrange
        filter_obj = FieldFilter(include_fields=set(), use_base=False)

        # Act
        result = filter_obj.fields

        # Assert
        assert result == set()


@pytest.mark.unit
class TestFilterDict:
    """Test filter_dict method."""

    def test_filter_dict_includes_only_specified_fields(self):
        """Test that filter_dict includes only fields in filter."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)
        data = {"name": "Product", "price": 10.99, "description": "Test", "id": 123}

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert result == {"name": "Product", "price": 10.99}
        assert "description" not in result
        assert "id" not in result

    def test_filter_dict_with_base_schema(self):
        """Test filter_dict with base schema."""
        # Arrange
        filter_obj = FieldFilter()
        data = {
            "name": "Product",
            "shop_name": "Biedronka",
            "price": 10.99,
            "valid_from": "2025-01-01",
            "description": "Test",
            "id": 123,
        }

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert "name" in result
        assert "shop_name" in result
        assert "price" in result
        assert "valid_from" in result
        assert "description" not in result
        assert "id" not in result

    def test_filter_dict_empty_dict(self):
        """Test filter_dict with empty dictionary."""
        # Arrange
        filter_obj = FieldFilter()
        data = {}

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert result == {}

    def test_filter_dict_no_matching_fields(self):
        """Test filter_dict when no fields match."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)
        data = {"description": "Test", "id": 123, "category": "Food"}

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert result == {}

    def test_filter_dict_all_fields_match(self):
        """Test filter_dict when all fields match."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)
        data = {"name": "Product", "price": 10.99}

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert result == {"name": "Product", "price": 10.99}

    def test_filter_dict_preserves_values(self):
        """Test that filter_dict preserves original values."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price", "active"}, use_base=False)
        data = {"name": "Product", "price": 10.99, "active": True}

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert result["name"] == "Product"
        assert result["price"] == 10.99
        assert result["active"] is True


@pytest.mark.unit
class TestFilterEntity:
    """Test filter_entity method."""

    def test_filter_entity_with_dict(self):
        """Test filter_entity with plain dictionary."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)
        data = {"name": "Product", "price": 10.99, "description": "Test"}

        # Act
        result = filter_obj.filter_entity(data)

        # Assert
        assert result == {"name": "Product", "price": 10.99}

    def test_filter_entity_with_pydantic_model(self):
        """Test filter_entity with Pydantic BaseModel."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)

        class Product(BaseModel):
            name: str
            price: float
            description: str
            id: int

        product = Product(name="Product", price=10.99, description="Test", id=123)

        # Act
        result = filter_obj.filter_entity(product)

        # Assert
        assert result == {"name": "Product", "price": 10.99}

    def test_filter_entity_with_dataclass(self):
        """Test filter_entity with dataclass."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)

        @dataclass
        class Product:
            name: str
            price: float
            description: str
            id: int

        product = Product(name="Product", price=10.99, description="Test", id=123)

        # Act
        result = filter_obj.filter_entity(product)

        # Assert
        assert result == {"name": "Product", "price": 10.99}

    def test_filter_entity_with_object_having_dict(self):
        """Test filter_entity with object having __dict__ attribute."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)

        class Product:
            def __init__(self, name, price, description):
                self.name = name
                self.price = price
                self.description = description

        product = Product(name="Product", price=10.99, description="Test")

        # Act
        result = filter_obj.filter_entity(product)

        # Assert
        assert result == {"name": "Product", "price": 10.99}

    def test_filter_entity_with_unsupported_type(self):
        """Test filter_entity raises TypeError for unsupported types."""
        # Arrange
        filter_obj = FieldFilter()

        # Act & Assert
        with pytest.raises(TypeError, match="Cannot filter entity of type"):
            filter_obj.filter_entity(123)

    def test_filter_entity_with_none(self):
        """Test filter_entity with None value."""
        # Arrange
        filter_obj = FieldFilter()

        # Act & Assert
        with pytest.raises(TypeError, match="Cannot filter entity of type"):
            filter_obj.filter_entity(None)


@pytest.mark.unit
class TestFilterMany:
    """Test filter_many method."""

    def test_filter_many_list_of_dicts(self):
        """Test filter_many with list of dictionaries."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)
        entities = [
            {"name": "Product1", "price": 10.99, "description": "Test1"},
            {"name": "Product2", "price": 20.99, "description": "Test2"},
            {"name": "Product3", "price": 30.99, "description": "Test3"},
        ]

        # Act
        result = filter_obj.filter_many(entities)

        # Assert
        expected = [
            {"name": "Product1", "price": 10.99},
            {"name": "Product2", "price": 20.99},
            {"name": "Product3", "price": 30.99},
        ]
        assert result == expected

    def test_filter_many_list_of_pydantic_models(self):
        """Test filter_many with list of Pydantic models."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)

        class Product(BaseModel):
            name: str
            price: float
            description: str

        entities = [
            Product(name="Product1", price=10.99, description="Test1"),
            Product(name="Product2", price=20.99, description="Test2"),
        ]

        # Act
        result = filter_obj.filter_many(entities)

        # Assert
        expected = [
            {"name": "Product1", "price": 10.99},
            {"name": "Product2", "price": 20.99},
        ]
        assert result == expected

    def test_filter_many_empty_list(self):
        """Test filter_many with empty list."""
        # Arrange
        filter_obj = FieldFilter()
        entities = []

        # Act
        result = filter_obj.filter_many(entities)

        # Assert
        assert result == []

    def test_filter_many_single_item(self):
        """Test filter_many with single item."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name"}, use_base=False)
        entities = [{"name": "Product", "price": 10.99}]

        # Act
        result = filter_obj.filter_many(entities)

        # Assert
        assert result == [{"name": "Product"}]


@pytest.mark.unit
class TestClassMethods:
    """Test FieldFilter class methods."""

    def test_minimal_class_method(self):
        """Test minimal class method creates filter with minimal fields."""
        # Act
        filter_obj = FieldFilter.minimal()

        # Assert
        assert filter_obj.fields == {"name", "price", "shop_name"}

    def test_with_dates_class_method(self):
        """Test with_dates class method creates filter with base schema."""
        # Act
        filter_obj = FieldFilter.with_dates()

        # Assert
        assert filter_obj.fields == FieldFilter.BASE_SCHEMA

    def test_custom_class_method(self):
        """Test custom class method creates filter with specified fields."""
        # Act
        filter_obj = FieldFilter.custom("name", "price", "custom_field")

        # Assert
        assert filter_obj.fields == {"name", "price", "custom_field"}

    def test_custom_class_method_single_field(self):
        """Test custom class method with single field."""
        # Act
        filter_obj = FieldFilter.custom("name")

        # Assert
        assert filter_obj.fields == {"name"}

    def test_custom_class_method_no_fields(self):
        """Test custom class method with no fields."""
        # Act
        filter_obj = FieldFilter.custom()

        # Assert
        assert filter_obj.fields == set()

    def test_extended_class_method(self):
        """Test extended class method adds fields to base schema."""
        # Act
        filter_obj = FieldFilter.extended("custom_field1", "custom_field2")

        # Assert
        expected = FieldFilter.BASE_SCHEMA | {"custom_field1", "custom_field2"}
        assert filter_obj.fields == expected

    def test_extended_class_method_no_extra_fields(self):
        """Test extended class method with no extra fields."""
        # Act
        filter_obj = FieldFilter.extended()

        # Assert
        assert filter_obj.fields == FieldFilter.BASE_SCHEMA


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_filter_dict_with_none_values(self):
        """Test filter_dict handles None values correctly."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)
        data = {"name": None, "price": None, "description": "Test"}

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert result == {"name": None, "price": None}

    def test_filter_dict_with_complex_values(self):
        """Test filter_dict handles complex value types."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "tags", "metadata"}, use_base=False)
        data = {
            "name": "Product",
            "tags": ["tag1", "tag2"],
            "metadata": {"key": "value"},
            "description": "Test",
        }

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert result["name"] == "Product"
        assert result["tags"] == ["tag1", "tag2"]
        assert result["metadata"] == {"key": "value"}

    def test_filter_dict_with_special_characters_in_keys(self):
        """Test filter_dict handles special characters in keys."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "field_name"}, use_base=False)
        data = {"name": "Product", "field_name": "value", "description": "Test"}

        # Act
        result = filter_obj.filter_dict(data)

        # Assert
        assert result == {"name": "Product", "field_name": "value"}

    def test_filter_entity_pydantic_with_optional_fields(self):
        """Test filter_entity with Pydantic model having optional fields."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)

        from typing import Optional

        class Product(BaseModel):
            name: str
            price: Optional[float] = None
            description: Optional[str] = None

        product = Product(name="Product", description="Test")

        # Act
        result = filter_obj.filter_entity(product)

        # Assert
        assert result == {"name": "Product", "price": None}

    def test_filter_many_mixed_entity_types(self):
        """Test filter_many with mixed entity types."""
        # Arrange
        filter_obj = FieldFilter(include_fields={"name", "price"}, use_base=False)

        class Product(BaseModel):
            name: str
            price: float
            description: str

        entities = [
            {"name": "Product1", "price": 10.99, "description": "Test1"},
            Product(name="Product2", price=20.99, description="Test2"),
        ]

        # Act
        result = filter_obj.filter_many(entities)

        # Assert
        expected = [
            {"name": "Product1", "price": 10.99},
            {"name": "Product2", "price": 20.99},
        ]
        assert result == expected

    def test_base_schema_is_immutable(self):
        """Test that modifying filter fields doesn't affect base schema."""
        # Arrange
        filter_obj = FieldFilter()
        original_base = FieldFilter.BASE_SCHEMA.copy()

        # Act
        filter_obj.fields.add("custom_field")

        # Assert
        assert FieldFilter.BASE_SCHEMA == original_base
        assert "custom_field" not in FieldFilter.BASE_SCHEMA
